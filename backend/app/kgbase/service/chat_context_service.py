from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Sequence
from functools import lru_cache
from typing import Any

import tiktoken
from sqlalchemy import select

from backend.app.kgbase.model.chat_library import ChatLibrary, ChatMessage
from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db_mysql import async_db_session

CHAT_CONTEXT_STATE_KEY = '_chat_context'
SUMMARY_SYSTEM_PROMPT = (
    '你是对话记忆压缩器。只能总结输入中明确出现的信息，不得补充、猜测或改写事实。'
    '删除寒暄、重复内容和冗余描述，保留对后续交流有用的信息。'
)
SUMMARY_REQUIREMENTS = """请把旧摘要与新增旧对话合并为一份滚动摘要，只保留：
1. 当前讨论主题；
2. 用户已经问过的问题；
3. 已经确认的信息；
4. 重要实体及其关系；
5. 用户提出的限制条件；
6. 用户对回答的纠正；
7. 尚未解决的问题；
8. 重要名称、日期、数字和否定关系。

不要添加输入中不存在的信息，不要保留寒暄、重复内容或 AI 回答中的冗余描述。只输出摘要正文。"""

ProgressCallback = Callable[[str, str], Awaitable[None] | None]


@lru_cache(maxsize=1)
def _token_encoder():
    return tiktoken.get_encoding('cl100k_base')


def count_tokens(text: str | None) -> int:
    return len(_token_encoder().encode(text or ''))


def truncate_tokens(text: str, limit: int) -> str:
    if limit <= 0:
        return ''
    tokens = _token_encoder().encode(text or '')
    if len(tokens) <= limit:
        return text
    return _token_encoder().decode(tokens[:limit]).rstrip()


def reset_chat_context_state(metadata: Any) -> dict[str, Any]:
    state = dict(metadata) if isinstance(metadata, dict) else {}
    state.pop(CHAT_CONTEXT_STATE_KEY, None)
    return state


class ChatContextService:
    @staticmethod
    def _message_dict(message: ChatMessage | dict[str, Any]) -> dict[str, Any]:
        if isinstance(message, dict):
            return message
        return {
            'role': message.role,
            'content': message.content,
            'sequence': message.sequence,
        }

    @classmethod
    def complete_turns(
        cls,
        messages: Sequence[ChatMessage | dict[str, Any]],
    ) -> list[list[dict[str, Any]]]:
        turns: list[list[dict[str, Any]]] = []
        pending_user: dict[str, Any] | None = None
        for raw_message in messages:
            message = cls._message_dict(raw_message)
            role = message.get('role')
            if role == 'user':
                pending_user = message
            elif role == 'assistant' and pending_user is not None:
                turns.append([pending_user, message])
                pending_user = None
        return turns

    @staticmethod
    def flatten_turns(turns: Sequence[Sequence[dict[str, Any]]]) -> list[dict[str, str]]:
        return [
            {'role': message['role'], 'content': str(message.get('content') or '')}
            for turn in turns
            for message in turn
        ]

    @staticmethod
    def partition_turns(
        turns: Sequence[Sequence[dict[str, Any]]],
        recent_limit: int,
    ) -> tuple[list[Sequence[dict[str, Any]]], list[Sequence[dict[str, Any]]]]:
        limit = max(1, recent_limit)
        return list(turns[:-limit]), list(turns[-limit:])

    @staticmethod
    def history_tokens(turns: Sequence[Sequence[dict[str, Any]]]) -> int:
        return sum(count_tokens(str(message.get('content') or '')) + 4 for turn in turns for message in turn)

    @staticmethod
    def model_context_limit(model: str) -> int:
        normalized = (model or '').strip().lower()
        matches = [
            (prefix.lower(), limit)
            for prefix, limit in settings.CHAT_CONTEXT_MODEL_LIMITS.items()
            if normalized.startswith(prefix.lower())
        ]
        if matches:
            return max(matches, key=lambda item: len(item[0]))[1]
        return settings.CHAT_CONTEXT_DEFAULT_MODEL_LIMIT

    @staticmethod
    async def _report(callback: ProgressCallback | None, message: str, detail: str) -> None:
        if callback is None:
            return
        result = callback(message, detail)
        if inspect.isawaitable(result):
            await result

    @staticmethod
    def _summary_input(summary: str, messages: Sequence[dict[str, Any]]) -> str:
        history = '\n'.join(
            f'{"用户" if message.get("role") == "user" else "AI"}：{message.get("content") or ""}'
            for message in messages
        )
        return f'旧摘要：\n{summary or "（无）"}\n\n本次新进入旧对话区域的内容：\n{history}\n\n{SUMMARY_REQUIREMENTS}'

    @staticmethod
    def _context_preview(summary: str, turns: Sequence[Sequence[dict[str, Any]]]) -> str:
        def compact(value: Any, limit: int = 180) -> str:
            text = ' '.join(str(value or '').split())
            return text if len(text) <= limit else f'{text[:limit].rstrip()}…'

        lines = [f'已使用 {len(turns)} 轮历史对话']
        if summary:
            lines.extend(['', '历史摘要', compact(summary)])
        for index, turn in enumerate(turns, start=1):
            user = next((message for message in turn if message.get('role') == 'user'), {})
            assistant = next((message for message in turn if message.get('role') == 'assistant'), {})
            lines.extend([
                '',
                f'第 {index} 轮',
                f'用户：{compact(user.get("content"))}',
                f'回答：{compact(assistant.get("content"))}',
            ])
        return '\n'.join(lines)

    @staticmethod
    def _state(metadata: Any) -> dict[str, Any]:
        if not isinstance(metadata, dict):
            return {}
        state = metadata.get(CHAT_CONTEXT_STATE_KEY)
        return dict(state) if isinstance(state, dict) else {}

    @staticmethod
    async def _load_history(
        *,
        chat_library_uuid: str,
        current_message_uuid: str | None,
        user_uuid: str,
    ) -> tuple[dict[str, Any], list[ChatMessage]]:
        async with async_db_session() as db:
            library_result = await db.execute(
                select(ChatLibrary).where(
                    ChatLibrary.uuid == chat_library_uuid,
                    ChatLibrary.user_uuid == user_uuid,
                )
            )
            library = library_result.scalars().first()
            if not library:
                raise errors.NotFoundError(msg='对话不存在')

            cutoff_sequence: int | None = None
            if current_message_uuid:
                current_result = await db.execute(
                    select(ChatMessage.sequence).where(
                        ChatMessage.uuid == current_message_uuid,
                        ChatMessage.chat_library_uuid == chat_library_uuid,
                        ChatMessage.role == 'user',
                    )
                )
                cutoff_sequence = current_result.scalar_one_or_none()

            statement = select(ChatMessage).where(ChatMessage.chat_library_uuid == chat_library_uuid)
            if cutoff_sequence is not None:
                statement = statement.where(ChatMessage.sequence < cutoff_sequence)
            statement = statement.order_by(ChatMessage.sequence, ChatMessage.created_time)
            message_result = await db.execute(statement)
            metadata = dict(library.messages) if isinstance(library.messages, dict) else {}
            return metadata, list(message_result.scalars().all())

    @staticmethod
    async def _save_summary(
        *,
        chat_library_uuid: str,
        user_uuid: str,
        summary: str,
        summarized_through_sequence: int,
    ) -> None:
        async with async_db_session.begin() as db:
            result = await db.execute(
                select(ChatLibrary)
                .where(
                    ChatLibrary.uuid == chat_library_uuid,
                    ChatLibrary.user_uuid == user_uuid,
                )
                .with_for_update()
            )
            library = result.scalars().first()
            if not library:
                raise errors.NotFoundError(msg='对话不存在')
            metadata = dict(library.messages) if isinstance(library.messages, dict) else {}
            metadata[CHAT_CONTEXT_STATE_KEY] = {
                'summary': summary,
                'summarized_through_sequence': summarized_through_sequence,
                'summary_tokens': count_tokens(summary),
            }
            library.messages = metadata

    @classmethod
    async def prepare(
        cls,
        *,
        chat_library_uuid: str,
        current_message_uuid: str | None,
        user_uuid: str,
        current_question: str,
        knowledge_context: str,
        system_prompt: str,
        api_key: str,
        base_url: str,
        model: str,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        metadata, stored_messages = await cls._load_history(
            chat_library_uuid=chat_library_uuid,
            current_message_uuid=current_message_uuid,
            user_uuid=user_uuid,
        )
        turns = cls.complete_turns(stored_messages)
        state = cls._state(metadata)
        summary = str(state.get('summary') or '')
        summarized_through = int(state.get('summarized_through_sequence') or 0)
        recent_limit = max(1, settings.CHAT_CONTEXT_RECENT_TURNS)
        old_turns, recent_turns = cls.partition_turns(turns, recent_limit)
        unsummarized_recent_turns = [
            turn
            for turn in recent_turns
            if max(int(message.get('sequence') or 0) for message in turn) > summarized_through
        ]
        raw_history_tokens = cls.history_tokens(turns)
        model_limit = cls.model_context_limit(model)
        trigger_ratio = min(1.0, max(0.1, settings.CHAT_CONTEXT_TRIGGER_RATIO))
        budget = max(1, int(model_limit * trigger_ratio))
        all_history_messages = cls.flatten_turns(turns)
        estimated_full_tokens = (
            count_tokens(system_prompt)
            + count_tokens(summary)
            + sum(count_tokens(message['content']) + 4 for message in all_history_messages)
            + count_tokens(knowledge_context)
            + count_tokens(current_question)
            + 24
        )

        await cls._report(
            progress_callback,
            '正在检查多轮对话上下文',
            f'已读取 {len(turns)} 轮历史对话，约 {raw_history_tokens} Token',
        )

        should_compress = bool(old_turns) and (
            raw_history_tokens > settings.CHAT_CONTEXT_COMPRESSION_THRESHOLD_TOKENS
            or estimated_full_tokens > budget
            or bool(summary)
        )
        selected_turns = unsummarized_recent_turns if summary else turns
        if should_compress:
            new_old_messages = [
                message
                for turn in old_turns
                for message in turn
                if int(message.get('sequence') or 0) > summarized_through
            ]
            if new_old_messages:
                await cls._report(
                    progress_callback,
                    '正在压缩历史对话',
                    f'滚动合并 {len(new_old_messages)} 条旧消息，最近 {len(recent_turns)} 轮保留原文',
                )
                try:
                    result = await GenericResponseGetter.get_response(
                        api_key=api_key,
                        base_url=base_url,
                        model=model,
                        messages=[
                            {'role': 'system', 'content': SUMMARY_SYSTEM_PROMPT},
                            {'role': 'user', 'content': cls._summary_input(summary, new_old_messages)},
                        ],
                        max_tokens=settings.CHAT_CONTEXT_SUMMARY_MAX_TOKENS,
                    )
                    summary = truncate_tokens(result or '', settings.CHAT_CONTEXT_SUMMARY_MAX_TOKENS)
                    if not summary:
                        raise ValueError('历史摘要为空')
                    summarized_through = max(int(message.get('sequence') or 0) for message in new_old_messages)
                    await cls._save_summary(
                        chat_library_uuid=chat_library_uuid,
                        user_uuid=user_uuid,
                        summary=summary,
                        summarized_through_sequence=summarized_through,
                    )
                    await cls._report(
                        progress_callback,
                        '历史对话压缩完成',
                        f'摘要约 {count_tokens(summary)} Token，最近 {len(recent_turns)} 轮保持完整',
                    )
                    selected_turns = [
                        turn
                        for turn in recent_turns
                        if max(int(message.get('sequence') or 0) for message in turn) > summarized_through
                    ]
                except Exception:
                    await cls._report(
                        progress_callback,
                        '历史对话压缩未完成',
                        '本轮继续使用原始历史消息生成回答',
                    )
                    summary = ''
                    selected_turns = turns
            else:
                selected_turns = unsummarized_recent_turns

        selected_turns = list(selected_turns)

        def estimate(context_text: str) -> int:
            return (
                count_tokens(system_prompt)
                + count_tokens(summary)
                + cls.history_tokens(selected_turns)
                + count_tokens(context_text)
                + count_tokens(current_question)
                + 24
            )

        removed_turns = 0
        while len(selected_turns) > 2 and estimate(knowledge_context) > budget:
            selected_turns.pop(0)
            removed_turns += 1

        context_for_answer = knowledge_context
        if estimate(context_for_answer) > budget:
            fixed_tokens = estimate('')
            context_for_answer = truncate_tokens(knowledge_context, max(0, budget - fixed_tokens))

        if removed_turns or context_for_answer != knowledge_context:
            await cls._report(
                progress_callback,
                '正在调整上下文长度',
                f'已移除最早 {removed_turns} 轮完整对话，并保留最相关的知识图谱检索内容',
            )

        if summary or selected_turns:
            await cls._report(
                progress_callback,
                '检索到的对话上下文',
                cls._context_preview(summary, selected_turns),
            )

        return {
            'summary': summary,
            'messages': cls.flatten_turns(selected_turns),
            'knowledge_context': context_for_answer,
            'history_tokens': raw_history_tokens,
            'estimated_tokens': estimate(context_for_answer),
            'context_budget': budget,
        }


chat_context_service = ChatContextService()
