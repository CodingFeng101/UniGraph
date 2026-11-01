import asyncio
from types import SimpleNamespace

from backend.common.core_layer.unigraph.module import kg_constructor as constructor_module
from backend.common.core_layer.unigraph.module.kg_constructor import SemanticKGConstructor


def test_extract_kg_reads_every_uploaded_file(tmp_path, monkeypatch) -> None:
    # Each file's chunks are numbered from 0, so merging them by index used to keep only the last file.
    (tmp_path / 'a.txt').write_text('第一份文档：立式加工中心的主轴单元。', encoding='utf-8')
    (tmp_path / 'b.txt').write_text('第二份文档：设备维修工负责主轴保养。', encoding='utf-8')
    (tmp_path / 'c.txt').write_text('第三份文档：刀库换刀卡滞的处理记录。', encoding='utf-8')
    seen = []

    async def fake_process_chunk(self, chunk, *_args):
        seen.append(chunk)
        return [], []

    monkeypatch.setattr(SemanticKGConstructor, '_process_chunk', fake_process_chunk)
    monkeypatch.setattr(constructor_module, 'task_progress', lambda *args, **kwargs: None)
    constructor = SemanticKGConstructor(kg_schema=[], schema_definition={})

    asyncio.run(constructor.extract_kg(str(tmp_path), 'key', 'https://example.com/v1', 'model', SimpleNamespace()))

    text = '\n'.join(str(chunk) for chunk in seen)
    assert all(marker in text for marker in ('第一份文档', '第二份文档', '第三份文档'))
