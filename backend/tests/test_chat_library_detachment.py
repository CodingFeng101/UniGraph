from backend.app.kgbase.model.chat_library import ChatLibrary


def test_chat_library_keeps_an_independent_owner_and_detaches_on_knowledge_base_delete() -> None:
    table = ChatLibrary.__table__

    assert table.c.user_uuid.nullable is False
    assert table.c.kg_base_uuid.nullable is True

    foreign_key = next(iter(table.c.kg_base_uuid.foreign_keys))
    assert foreign_key.ondelete == 'SET NULL'
