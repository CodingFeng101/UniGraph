from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key
from backend.database.db_mysql import uuid4_str


class LlmModel(Base):
    """大模型表"""

    __tablename__ = 'llm_model'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True)
    # 外键关系
    provider_uuid: Mapped[str] = mapped_column(ForeignKey('llm_provider.uuid'), nullable=False, comment='提供商UUID')
    type: Mapped[str] = mapped_column(String(50), comment='模型类型')
    name: Mapped[str] = mapped_column(String(255), comment='模型名称')
    group_name: Mapped[Optional[str]] = mapped_column(String(100), comment='分组名称')
    status: Mapped[int] = mapped_column(default=1, comment='状态(0停用 1正常)')

    # provider: Mapped["LlmProvider"] = relationship(
    #     'LlmProvider',
    #     back_populates="models",
    #     init=False
    # )
