from datetime import datetime
from typing import List, Optional

from pydantic import Field, model_validator

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


# ================= Provider Schemas =================
class LlmProviderSchemaBase(SchemaBase):
    name: str = Field(..., max_length=255, description='提供商名称')
    api_key: Optional[str] = Field('', description='API密钥')
    api_url: Optional[str] = Field('', max_length=512, description='API地址')
    document_url: Optional[str] = Field(None, max_length=512, description='文档URL')
    llm_model_url: Optional[str] = Field(None, max_length=512, description='模型URL')
    status: Optional[int] = Field(None, description='状态(0停用 1正常)')


class LlmProviderListSchema(LlmProviderSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    created_time: datetime
    updated_time: Optional[datetime] = None
    sort_order: int = 0

    @model_validator(mode='after')
    def format_urls(self):
        """空URL转为占位符"""
        self.api_key = '********' if self.api_key else ''
        self.document_url = self.document_url or '--'
        self.llm_model_url = self.llm_model_url or '--'
        return self


class CreateLlmProviderParam(SchemaBase):
    user_uuid: str = Field(..., description='关联用户UUID')
    name: str = Field(..., max_length=255, description='提供商名称')
    api_key: Optional[str] = Field('', description='API密钥')
    api_url: Optional[str] = Field('', max_length=512, description='API地址')
    document_url: Optional[str] = Field('', max_length=512, description='文档URL')
    llm_model_url: Optional[str] = Field('', max_length=512, description='模型URL')

    @model_validator(mode='before')
    def sanitize_urls(cls, values):
        """清理空URL字段"""
        values.setdefault('user_uuid', 'example')
        values.setdefault('document_url', '')
        values.setdefault('llm_model_url', '')
        return values


class UpdateLlmProviderParam(SchemaBase):
    name: Optional[str] = Field(None, max_length=255, description='提供商名称')
    api_key: Optional[str] = Field(None, description='API密钥')
    api_url: Optional[str] = Field(None, max_length=512, description='API地址')
    document_url: Optional[str] = Field(None, max_length=512, description='文档URL')
    llm_model_url: Optional[str] = Field(None, max_length=512, description='模型URL')
    status: Optional[int] = Field(None, description='状态(0停用 1正常)')


class ReorderLlmProviderParam(SchemaBase):
    provider_uuids: List[str] = Field(..., min_length=1, description='按目标顺序排列的提供商 UUID')


# ================= Model Schemas =================
class LlmModelSchemaBase(SchemaBase):
    type: str = Field(..., description='模型类型')  # 使用枚举类型
    name: str = Field(..., max_length=255, description='模型名称')
    group_name: Optional[str] = Field(None, max_length=100, description='分组名称')
    status: int = Field(default=StatusType.enable.value, description='状态(0停用 1正常)')


class LlmModelDetailSchema(LlmModelSchemaBase):
    id: int
    uuid: str
    provider_uuid: str = Field(..., description='关联提供商UUID')
    created_time: datetime
    updated_time: Optional[datetime] = None
    provider_info: 'LlmProviderSimpleSchema' = Field(description='提供商基础信息')


class LlmModelListSchema(LlmModelSchemaBase):
    id: int
    uuid: str
    provider_uuid: str = Field(..., description='关联提供商UUID')
    created_time: datetime
    updated_time: Optional[datetime] = None

    @model_validator(mode='after')
    def format_group(self):
        """处理空分组显示"""
        self.group_name = self.group_name or '未分组'
        return self


class CreateLlmModelParam(LlmModelSchemaBase):
    provider_uuid: str = Field(..., description='关联提供商UUID')  # 修正字段名

    @model_validator(mode='before')
    def set_default_group(cls, values):
        """设置默认分组"""
        if not values.get('group_name'):
            values['group_name'] = '默认分组'
        return values


class UpdateLlmModelParam(SchemaBase):
    type: Optional[str] = Field(None, description='模型类型')
    name: Optional[str] = Field(None, max_length=255, description='模型名称')
    group_name: Optional[str] = Field(None, max_length=100, description='分组名称')
    status: Optional[int] = Field(None, description='状态(0停用 1正常)')


# ================= Helper Schemas =================
class LlmProviderSimpleSchema(SchemaBase):
    uuid: str
    name: str
    api_url: str


class LlmModelSimpleSchema(SchemaBase):
    uuid: str
    name: str
    type: str


class LlmProviderDetailSchema(LlmProviderSchemaBase):
    id: int
    uuid: str
    user_uuid: str
    models: List[LlmModelListSchema]
    created_time: datetime
    updated_time: Optional[datetime] = None
    sort_order: int = 0

    @model_validator(mode='after')
    def mask_api_key(self):
        self.api_key = '********' if self.api_key else ''
        return self

    # List['LlmModelSimpleSchema'] = Field(default_factory=list, description="关联模型列表")


# 解决前向引用问题
LlmProviderDetailSchema.model_rebuild()
LlmModelDetailSchema.model_rebuild()
