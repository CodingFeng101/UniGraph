import backend.app.admin.model  # noqa: F401
from backend.app.admin.model.sys_user import User
from sqlalchemy.orm import configure_mappers


def test_admin_models_are_registered() -> None:
    configure_mappers()
    assert User.llm_models.property.mapper.class_.__name__ == 'LlmProvider'
