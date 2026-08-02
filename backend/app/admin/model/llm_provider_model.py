from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.admin.model.llm_model import LlmModel
from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str


class LlmProvider(Base):
    """大模型提供商表"""

    __tablename__ = 'llm_provider'
    __table_args__ = (UniqueConstraint('user_uuid', 'name', name='uq_llm_provider_user_name'),)
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    # 外键关系
    user_uuid: Mapped[str] = mapped_column(ForeignKey('sys_user.uuid'), nullable=False, comment='用户UUID')
    name: Mapped[str] = mapped_column(String(255), comment='提供商名称')
    api_key: Mapped[str] = mapped_column(Text, comment='加密后的 API 密钥')
    api_url: Mapped[str] = mapped_column(String(512), comment='API地址')
    document_url: Mapped[Optional[str]] = mapped_column(String(512), comment='文档URL')
    llm_model_url: Mapped[Optional[str]] = mapped_column(String(512), comment='模型URL')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # 关系定义
    models: Mapped[List['LlmModel']] = relationship(
        'LlmModel',
        # back_populates="provider",
        cascade='all, delete-orphan',
        init=False,
    )
