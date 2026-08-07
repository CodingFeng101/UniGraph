import _env  # noqa: F401  # isort: skip
import unittest
from unittest.mock import AsyncMock, Mock, patch

from backend.app.kgbase.service.chat_context_service import (
    ChatContextService,
    count_tokens,
    reset_chat_context_state,
    truncate_tokens,
)
from backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.search import (
    LocalSearch,
)


def message(role: str, content: str, sequence: int) -> dict:
    return {'role': role, 'content': content, 'sequence': sequence}


class ChatContextServiceTests(unittest.TestCase):
    def test_only_complete_user_assistant_pairs_become_turns(self):
        messages = [
            message('user', '问题一', 1),
            message('assistant', '回答一', 2),
            message('user', '当前问题', 3),
        ]

        turns = ChatContextService.complete_turns(messages)

        self.assertEqual(len(turns), 1)
        self.assertEqual([item['content'] for item in turns[0]], ['问题一', '回答一'])

    def test_recent_eight_turns_are_kept_verbatim(self):
        turns = [
            [message('user', f'问题{i}', i * 2 + 1), message('assistant', f'回答{i}', i * 2 + 2)] for i in range(10)
        ]

        old_turns, recent_turns = ChatContextService.partition_turns(turns, 8)

        self.assertEqual(len(old_turns), 2)
        self.assertEqual(len(recent_turns), 8)
        self.assertEqual(recent_turns[0][0]['content'], '问题2')
        self.assertEqual(recent_turns[-1][1]['content'], '回答9')

    def test_summary_prompt_only_contains_old_summary_and_new_old_messages(self):
        prompt = ChatContextService._summary_input(
            '已经确认甲与乙有关联',
            [message('user', '不要使用丙', 9), message('assistant', '已确认不使用丙', 10)],
        )

        self.assertIn('已经确认甲与乙有关联', prompt)
        self.assertIn('不要使用丙', prompt)
        self.assertIn('否定关系', prompt)

    def test_token_truncation_respects_limit(self):
        text = '知识图谱上下文' * 200
        truncated = truncate_tokens(text, 40)

        self.assertLessEqual(count_tokens(truncated), 40)
        self.assertTrue(truncated)

    def test_reset_removes_only_internal_context_state(self):
        metadata = {'legacy': 'value', '_chat_context': {'summary': '旧摘要'}}

        self.assertEqual(reset_chat_context_state(metadata), {'legacy': 'value'})


class LocalSearchConversationContextTests(unittest.IsolatedAsyncioTestCase):
    async def test_rolling_summary_only_merges_newly_aged_out_messages(self):
        turns = [
            [message('user', f'问题{i}', i * 2 + 1), message('assistant', f'回答{i}', i * 2 + 2)] for i in range(10)
        ]
        stored_messages = [item for turn in turns for item in turn]
        metadata = {
            '_chat_context': {
                'summary': '旧摘要内容',
                'summarized_through_sequence': 2,
            }
        }

        with (
            patch.object(
                ChatContextService,
                '_load_history',
                new=AsyncMock(return_value=(metadata, stored_messages)),
            ),
            patch.object(ChatContextService, '_save_summary', new=AsyncMock()) as save_summary,
            patch(
                'backend.app.kgbase.service.chat_context_service.GenericResponseGetter.get_response',
                new=AsyncMock(return_value='更新后的摘要'),
            ) as summarize,
        ):
            result = await ChatContextService.prepare(
                chat_library_uuid='chat-1',
                current_message_uuid='message-21',
                user_uuid='user-1',
                current_question='当前问题',
                knowledge_context='知识图谱结果',
                system_prompt='系统提示词',
                api_key='key',
                base_url='https://example.com',
                model='gpt-4o',
            )

        summary_input = summarize.await_args.kwargs['messages'][1]['content']
        self.assertIn('旧摘要内容', summary_input)
        self.assertNotIn('问题0', summary_input)
        self.assertIn('问题1', summary_input)
        self.assertNotIn('问题2', summary_input)
        self.assertEqual(result['summary'], '更新后的摘要')
        self.assertEqual(len(result['messages']), 16)
        save_summary.assert_awaited_once()
        self.assertEqual(save_summary.await_args.kwargs['summarized_through_sequence'], 4)

    async def test_history_is_only_added_after_current_question_retrieval(self):
        context_builder = AsyncMock()
        context_item = Mock()
        context_item.to_dict.return_value = {'id': 1}
        context_builder.build_context.return_value = ('完整图谱结果', {'Entities': context_item})
        search = LocalSearch(context_builder, 'KG:{context_data}\nQUESTION:{query}\nTYPE:{response_type}')
        context_provider = AsyncMock(
            return_value={
                'summary': '旧摘要',
                'messages': [
                    {'role': 'user', 'content': '上一问'},
                    {'role': 'assistant', 'content': '上一答'},
                ],
                'knowledge_context': '裁剪后的相关图谱结果',
            }
        )

        with (
            patch(
                'backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.search.extract_entities_from_query',
                new=AsyncMock(return_value=['当前实体']),
            ) as extract,
            patch(
                'backend.common.core_layer.unigraph.module.sapperrag.retriver.structured_search.local_search.search.GenericResponseGetter.get_response',
                new=AsyncMock(return_value='最终回答'),
            ) as get_response,
        ):
            result = await search.search(
                '当前问题',
                1,
                False,
                'key',
                'https://example.com',
                'model',
                context_provider=context_provider,
            )

        self.assertEqual(result, '最终回答')
        self.assertEqual(extract.await_args.args[0], '当前问题')
        context_provider.assert_awaited_once_with('完整图谱结果')
        messages = get_response.await_args.kwargs['messages']
        self.assertEqual([item['role'] for item in messages], ['system', 'system', 'user', 'assistant', 'user'])
        self.assertIn('旧摘要', messages[1]['content'])
        self.assertEqual(messages[2]['content'], '上一问')
        self.assertIn('裁剪后的相关图谱结果', messages[-1]['content'])
        self.assertIn('当前问题', messages[-1]['content'])


if __name__ == '__main__':
    unittest.main()
