import asyncio
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from backend.common.core_layer.unigraph.file.content_getter import FileContentGetterFactory
from backend.core.path_conf import FILES_DIR

MAX_ATTACHMENT_CHARS = 12_000
MAX_TOTAL_ATTACHMENT_CHARS = 24_000
SUPPORTED_EXTENSIONS = {'.csv', '.docx', '.json', '.md', '.pdf', '.txt'}


class ChatAttachmentService:
    @staticmethod
    def _resolve(url: str) -> Path:
        path = PurePosixPath(unquote(urlsplit(str(url or '')).path).lstrip('/'))
        if len(path.parts) < 3 or path.parts[0] != 'files':
            raise ValueError('Invalid chat attachment path')
        root = Path(FILES_DIR).resolve()
        candidate = (root / Path(*path.parts[1:])).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError('Invalid chat attachment path') from exc
        if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS or not candidate.is_file():
            raise ValueError('Chat attachment is unavailable or unsupported')
        return candidate

    @classmethod
    async def build_context(cls, attachments) -> str:
        sections: list[str] = []
        remaining = MAX_TOTAL_ATTACHMENT_CHARS
        for attachment in attachments or []:
            if remaining <= 0:
                break
            path = cls._resolve(attachment.url)
            getter = FileContentGetterFactory.create(str(path).lower())
            content = await asyncio.to_thread(getter.get_content, str(path))
            content = str(content or '').strip()
            if not content:
                raise ValueError(f'无法读取附件内容：{attachment.name}')
            excerpt = content[: min(MAX_ATTACHMENT_CHARS, remaining)]
            sections.append(f'附件“{attachment.name}”内容：\n{excerpt}')
            remaining -= len(excerpt)
        if not sections:
            return ''
        return '\n\n以下是用户本轮上传的附件内容，仅用于回答本轮问题：\n\n' + '\n\n'.join(sections)


chat_attachment_service = ChatAttachmentService()
