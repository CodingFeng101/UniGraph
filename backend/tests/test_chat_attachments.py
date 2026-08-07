import _env  # noqa: F401  # isort: skip
import asyncio

import pytest
from backend.app.kgbase.service import chat_attachment_service as module


def test_chat_attachment_content_is_added_to_question_context(tmp_path, monkeypatch) -> None:
    folder = tmp_path / 'upload-id'
    folder.mkdir()
    (folder / 'notes.md').write_text('附件中的关键结论', encoding='utf-8')
    monkeypatch.setattr(module, 'FILES_DIR', str(tmp_path))

    attachment = type('Attachment', (), {'name': 'notes.md', 'url': 'files/upload-id/notes.md'})()
    context = asyncio.run(module.chat_attachment_service.build_context([attachment]))

    assert 'notes.md' in context
    assert '附件中的关键结论' in context


def test_chat_attachment_cannot_escape_upload_root(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(module, 'FILES_DIR', str(tmp_path))
    attachment = type('Attachment', (), {'name': 'secret.txt', 'url': 'files/../secret.txt'})()

    with pytest.raises(ValueError, match='Invalid chat attachment path'):
        asyncio.run(module.chat_attachment_service.build_context([attachment]))
