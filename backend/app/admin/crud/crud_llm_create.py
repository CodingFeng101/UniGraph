from sqlalchemy.ext.asyncio import AsyncSession


class LlmCreateCRUD:
    @staticmethod
    async def create_providers(db: AsyncSession, objects: list, commit: bool = False):
        """
        批量创建 LlmProvider 记录
        :param db: 异步数据库会话
        :param objects: LlmProvider 对象列表
        :param commit: 是否立即提交事务
        """
        db.add_all(objects)
        if commit:
            await db.commit()
        else:
            await db.flush()

    @staticmethod
    async def create_models(db: AsyncSession, objects: list, commit: bool = False):
        """
        批量创建 LlmModel 记录
        :param db: 异步数据库会话
        :param objects: LlmModel 对象列表
        :param commit: 是否立即提交事务
        """
        db.add_all(objects)
        if commit:
            await db.commit()
        else:
            await db.flush()
