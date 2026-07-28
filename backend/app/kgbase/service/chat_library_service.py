#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json

from sqlalchemy import delete, func, select

from backend.app.kgbase.crud.crud_chat_library import library_dao
from backend.app.kgbase.model.chat_library import ChatLibrary, ChatMessage, ChatMessageSource, ChatShare
from backend.app.kgbase.schema.chat_library import AppendMessageParam, AppendTurnParam, LibraryBase, LibraryDetail
from backend.app.kgbase.service.llm_info_service import get_user_llm_info
from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from backend.common.exception import errors
from backend.database.db_mysql import async_db_session, uuid4_str


class ChatLibraryService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁
    MAX_SHARE_MESSAGES = 500
    MAX_SHARE_SNAPSHOT_BYTES = 5 * 1024 * 1024

    @staticmethod
    async def _get_owned_kg_base(db, kg_base_uuid: str, user_uuid: str):
        from backend.app.kgbase.model.kg_base import KgBase

        result = await db.execute(select(KgBase).where(KgBase.uuid == kg_base_uuid, KgBase.user_uuid == user_uuid))
        kg_base = result.scalars().first()
        if not kg_base:
            raise errors.NotFoundError(msg='知识库不存在')
        return kg_base

    @staticmethod
    async def _get_owned_library(
        db,
        chat_library_uuid: str,
        user_uuid: str,
        *,
        for_update: bool = False,
    ) -> ChatLibrary:
        from backend.app.kgbase.model.kg_base import KgBase

        statement = (
            select(ChatLibrary)
            .join(KgBase, ChatLibrary.kg_base_uuid == KgBase.uuid)
            .where(
                ChatLibrary.uuid == chat_library_uuid,
                KgBase.user_uuid == user_uuid,
            )
        )
        if for_update:
            # Serializes share mutations for one conversation, preventing two
            # simultaneous create requests from violating the unique key.
            statement = statement.with_for_update()
        result = await db.execute(statement)
        library = result.scalars().first()
        if not library:
            raise errors.NotFoundError(msg='对话不存在')
        return library

    @staticmethod
    async def add(*, obj: LibraryBase, user_uuid: str) -> str:
        async with async_db_session.begin() as db:
            await ChatLibraryService._get_owned_kg_base(db, obj.kg_base_uuid, user_uuid)
            return await library_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, user_uuid: str, obj: LibraryDetail) -> int:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)

            # 更新图谱库信息
            count = await library_dao.update_library(db, library.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{source.id}')
            return count

    @staticmethod
    async def get_library(*, uuid: str = None, name: str = None) -> ChatLibrary:
        async with async_db_session() as db:
            library = await library_dao.get_with_relation(db, uuid=uuid, name=name)
            if not library:
                raise errors.NotFoundError(msg='图谱库不存在')
            return library

    @staticmethod
    async def delete(*, uuid: str, user_uuid: str) -> int:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)
            message_uuids = select(ChatMessage.uuid).where(ChatMessage.chat_library_uuid == uuid)
            await db.execute(delete(ChatMessageSource).where(ChatMessageSource.message_uuid.in_(message_uuids)))
            await db.execute(delete(ChatMessage).where(ChatMessage.chat_library_uuid == uuid))
            count = await library_dao.delete(db, library.id)
            return count

    @staticmethod
    # async def update_status(*, request: Request, pk: int) -> int:
    #     async with async_db_session.begin() as db:
    #         superuser_verify(request)
    #         source = await source_dao.get(db, pk)
    #         if not source:
    #             raise errors.NotFoundError(msg='图谱库不存在')
    #         if pk == request.user.id:
    #             raise errors.ForbiddenError(msg='非法操作')
    #         status = await source_dao.get_status(db, pk)
    #         count = await source_dao.set_status(db, pk, False if status else True)
    #         await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{pk}')
    #         return count
    @staticmethod
    async def get_all(*, kg_base_uuid: str, user_uuid: str) -> list[ChatLibrary]:
        async with async_db_session() as db:
            await ChatLibraryService._get_owned_kg_base(db, kg_base_uuid, user_uuid)
            library = await library_dao.get_list(db, kg_base_uuid=kg_base_uuid)
            return library

    @staticmethod
    async def get_conversation(*, uuid: str, user_uuid: str) -> dict:
        async with async_db_session() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid)
            message_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.chat_library_uuid == uuid)
                .order_by(ChatMessage.sequence, ChatMessage.created_time)
            )
            messages = list(message_result.scalars().all())
            message_uuids = [message.uuid for message in messages]
            sources_by_message: dict[str, list[dict]] = {}
            if message_uuids:
                source_result = await db.execute(
                    select(ChatMessageSource)
                    .where(ChatMessageSource.message_uuid.in_(message_uuids))
                    .order_by(ChatMessageSource.position)
                )
                for source in source_result.scalars().all():
                    sources_by_message.setdefault(source.message_uuid, []).append({
                        'uuid': source.uuid,
                        'source_type': source.source_type,
                        'content': source.content,
                        'position': source.position,
                    })
            return {
                'uuid': library.uuid,
                'kg_base_uuid': library.kg_base_uuid,
                'name': library.name,
                'is_favorite': library.is_favorite,
                'messages': library.messages or {},
                'conversation': [
                    {
                        'uuid': message.uuid,
                        'role': message.role,
                        'content': message.content,
                        'sequence': message.sequence,
                        'knowledge_graph_uuid': message.knowledge_graph_uuid,
                        'model_name': message.model_name,
                        'effort': message.effort,
                        'created_time': message.created_time,
                        'sources': sources_by_message.get(message.uuid, []),
                    }
                    for message in messages
                ],
            }

    @staticmethod
    async def _build_share_snapshot(db, library: ChatLibrary) -> dict:
        message_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_library_uuid == library.uuid)
            .order_by(ChatMessage.sequence, ChatMessage.created_time)
            .limit(ChatLibraryService.MAX_SHARE_MESSAGES + 1)
        )
        messages = list(message_result.scalars().all())
        if len(messages) > ChatLibraryService.MAX_SHARE_MESSAGES:
            raise errors.RequestError(msg=f'对话超过 {ChatLibraryService.MAX_SHARE_MESSAGES} 条消息，暂时无法分享')
        message_uuids = [message.uuid for message in messages]
        sources_by_message: dict[str, list[dict]] = {}
        if message_uuids:
            source_result = await db.execute(
                select(ChatMessageSource)
                .where(ChatMessageSource.message_uuid.in_(message_uuids))
                .order_by(ChatMessageSource.position)
            )
            for source in source_result.scalars().all():
                sources_by_message.setdefault(source.message_uuid, []).append({
                    'source_type': source.source_type,
                    'content': source.content,
                    'position': source.position,
                })
        snapshot = {
            'title': library.name,
            'conversation': [
                {
                    'role': message.role,
                    'content': message.content,
                    'sequence': message.sequence,
                    'model_name': message.model_name,
                    'effort': message.effort,
                    'created_time': message.created_time.isoformat(),
                    'sources': sources_by_message.get(message.uuid, []),
                }
                for message in messages
            ],
        }
        snapshot_size = len(
            json.dumps(snapshot, ensure_ascii=False, separators=(',', ':'), default=str).encode('utf-8')
        )
        if snapshot_size > ChatLibraryService.MAX_SHARE_SNAPSHOT_BYTES:
            raise errors.RequestError(msg='对话内容超过 5 MB，暂时无法分享')
        return snapshot

    @staticmethod
    def _serialize_share(share: ChatShare) -> dict:
        return {
            'public_id': share.public_id,
            'title': share.title,
            'message_count': share.message_count,
            'is_active': share.is_active,
            'created_time': share.created_time,
            'updated_time': share.updated_time,
        }

    @staticmethod
    async def get_share(*, chat_library_uuid: str, user_uuid: str) -> dict | None:
        async with async_db_session() as db:
            await ChatLibraryService._get_owned_library(db, chat_library_uuid, user_uuid)
            result = await db.execute(select(ChatShare).where(ChatShare.chat_library_uuid == chat_library_uuid))
            share = result.scalars().first()
            return ChatLibraryService._serialize_share(share) if share and share.is_active else None

    @staticmethod
    async def create_share(*, chat_library_uuid: str, user_uuid: str) -> dict:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, chat_library_uuid, user_uuid, for_update=True)
            snapshot = await ChatLibraryService._build_share_snapshot(db, library)
            if not snapshot['conversation']:
                raise errors.ForbiddenError(msg='空对话不能分享')
            result = await db.execute(select(ChatShare).where(ChatShare.chat_library_uuid == chat_library_uuid))
            share = result.scalars().first()
            if share and share.is_active:
                return ChatLibraryService._serialize_share(share)
            if share:
                share.public_id = uuid4_str()
                share.title = library.name
                share.snapshot = snapshot
                share.message_count = len(snapshot['conversation'])
                share.is_active = True
            else:
                share = ChatShare(
                    chat_library_uuid=chat_library_uuid,
                    title=library.name,
                    snapshot=snapshot,
                    message_count=len(snapshot['conversation']),
                )
                db.add(share)
            await db.flush()
            return ChatLibraryService._serialize_share(share)

    @staticmethod
    async def update_share(*, chat_library_uuid: str, user_uuid: str) -> dict:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, chat_library_uuid, user_uuid, for_update=True)
            result = await db.execute(
                select(ChatShare).where(
                    ChatShare.chat_library_uuid == chat_library_uuid,
                    ChatShare.is_active.is_(True),
                )
            )
            share = result.scalars().first()
            if not share:
                raise errors.NotFoundError(msg='分享链接不存在')
            snapshot = await ChatLibraryService._build_share_snapshot(db, library)
            share.title = library.name
            share.snapshot = snapshot
            share.message_count = len(snapshot['conversation'])
            await db.flush()
            return ChatLibraryService._serialize_share(share)

    @staticmethod
    async def rotate_share(*, chat_library_uuid: str, user_uuid: str) -> dict:
        """Rotate the public identifier and capture the latest snapshot.

        The previous public URL becomes invalid as soon as this transaction is
        committed. This is intentionally separate from ``update_share`` so an
        owner can refresh shared content without unexpectedly breaking a link.
        """
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, chat_library_uuid, user_uuid, for_update=True)
            snapshot = await ChatLibraryService._build_share_snapshot(db, library)
            if not snapshot['conversation']:
                raise errors.ForbiddenError(msg='空对话不能分享')
            result = await db.execute(select(ChatShare).where(ChatShare.chat_library_uuid == chat_library_uuid))
            share = result.scalars().first()
            if not share:
                share = ChatShare(
                    chat_library_uuid=chat_library_uuid,
                    title=library.name,
                    snapshot=snapshot,
                    message_count=len(snapshot['conversation']),
                )
                db.add(share)
            else:
                share.public_id = uuid4_str()
                share.title = library.name
                share.snapshot = snapshot
                share.message_count = len(snapshot['conversation'])
                share.is_active = True
            await db.flush()
            return ChatLibraryService._serialize_share(share)

    @staticmethod
    async def revoke_share(*, chat_library_uuid: str, user_uuid: str) -> None:
        async with async_db_session.begin() as db:
            await ChatLibraryService._get_owned_library(db, chat_library_uuid, user_uuid, for_update=True)
            result = await db.execute(select(ChatShare).where(ChatShare.chat_library_uuid == chat_library_uuid))
            share = result.scalars().first()
            if share:
                share.is_active = False

    @staticmethod
    async def get_public_share(*, public_id: str) -> dict:
        async with async_db_session() as db:
            result = await db.execute(
                select(ChatShare).where(
                    ChatShare.public_id == public_id,
                    ChatShare.is_active.is_(True),
                )
            )
            share = result.scalars().first()
            if not share:
                raise errors.NotFoundError(msg='分享链接不存在或已失效')
            return {
                **share.snapshot,
                'public_id': share.public_id,
                'message_count': share.message_count,
                'shared_time': share.updated_time or share.created_time,
            }

    @staticmethod
    async def append_turn(*, uuid: str, user_uuid: str, obj: AppendTurnParam) -> dict:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)
            sequence_result = await db.execute(
                select(func.coalesce(func.max(ChatMessage.sequence), 0)).where(ChatMessage.chat_library_uuid == uuid)
            )
            next_sequence = int(sequence_result.scalar_one()) + 1
            user_message = ChatMessage(
                chat_library_uuid=uuid,
                role='user',
                content=obj.user_content,
                sequence=next_sequence,
                knowledge_graph_uuid=obj.knowledge_graph_uuid,
            )
            assistant_message = ChatMessage(
                chat_library_uuid=uuid,
                role='assistant',
                content=obj.assistant_content,
                sequence=next_sequence + 1,
                knowledge_graph_uuid=obj.knowledge_graph_uuid,
                model_name=obj.model_name,
                effort=obj.effort,
            )
            db.add_all([user_message, assistant_message])
            await db.flush()
            source_rows = []
            for position, source_type in enumerate(('Sources', 'Entities', 'Relationships', 'Communities')):
                content = obj.sources.get(source_type, [])
                source_rows.append(
                    ChatMessageSource(
                        message_uuid=assistant_message.uuid,
                        source_type=source_type,
                        content=content,
                        position=position,
                    )
                )
            db.add_all(source_rows)
            library.name = library.name or obj.user_content[:24]
            return {
                'user_message_uuid': user_message.uuid,
                'assistant_message_uuid': assistant_message.uuid,
            }

    @staticmethod
    async def append_message(*, uuid: str, user_uuid: str, obj: AppendMessageParam) -> dict:
        async with async_db_session.begin() as db:
            await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)
            sequence_result = await db.execute(
                select(func.coalesce(func.max(ChatMessage.sequence), 0)).where(ChatMessage.chat_library_uuid == uuid)
            )
            message = ChatMessage(
                chat_library_uuid=uuid,
                role=obj.role,
                content=obj.content,
                sequence=int(sequence_result.scalar_one()) + 1,
                knowledge_graph_uuid=obj.knowledge_graph_uuid,
                model_name=obj.model_name if obj.role == 'assistant' else None,
                effort=obj.effort if obj.role == 'assistant' else None,
            )
            db.add(message)
            await db.flush()
            if obj.role == 'assistant':
                db.add_all([
                    ChatMessageSource(
                        message_uuid=message.uuid,
                        source_type=source_type,
                        content=obj.sources.get(source_type, []),
                        position=position,
                    )
                    for position, source_type in enumerate(('Sources', 'Entities', 'Relationships', 'Communities'))
                ])
            return {'message_uuid': message.uuid}

    @staticmethod
    async def generate_title(*, uuid: str, content: str, user_token: str, user_uuid: str) -> str:
        async with async_db_session() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid)
            if not (library.name or '').startswith('新对话-'):
                return library.name

        api_key, base_url, model = await get_user_llm_info(user_token)
        result = await GenericResponseGetter.get_response(
            api_key=api_key,
            base_url=base_url,
            model=model,
            query=(
                f'把下面的用户需求概括成一个不超过12个汉字的中文标题。只输出标题，不要引号、标点或解释。\n\n{content}'
            ),
        )
        title = ''.join((result or '').strip().strip('"“”\'').splitlines())[:12] or content[:12]
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)
            if (library.name or '').startswith('新对话-'):
                library.name = title
                return title
            return library.name

    @staticmethod
    async def set_favorite(*, uuid: str, user_uuid: str, is_favorite: bool) -> int:
        async with async_db_session.begin() as db:
            library = await ChatLibraryService._get_owned_library(db, uuid, user_uuid, for_update=True)
            library.is_favorite = is_favorite
            return 1


chat_library_service = ChatLibraryService()
