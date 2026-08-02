from abc import ABC, abstractmethod
from typing import Any

from openai import AsyncOpenAI

# semaphore = asyncio.Semaphore(100)  # 控制最大并发任务数为 100


class ResponseGetter(ABC):
    @abstractmethod
    def get_response(self, **kwargs):
        pass

    @abstractmethod
    def get_vector(self, **kwargs):
        pass


class GenericResponseGetter(ResponseGetter):
    @staticmethod
    def _chat_request(
        *, query: str, model: str, messages: list[dict[str, str]] | None, max_tokens: int | None
    ) -> dict[str, Any]:
        request: dict[str, Any] = {
            'model': model,
            'messages': messages
            or [
                {'role': 'system', 'content': '你是知识图谱领域专家。'},
                {'role': 'user', 'content': query},
            ],
            'temperature': 0,
        }
        if max_tokens is not None:
            token_parameter = (
                'max_completion_tokens' if model.lower().startswith(('gpt-5', 'o1', 'o3')) else 'max_tokens'
            )
            request[token_parameter] = max_tokens
        return request

    @staticmethod
    async def get_response(
        api_key: str,
        base_url: str,
        query: str = '',
        model: str = 'deepseek-v3-250324',
        messages: list[dict[str, str]] | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """
        聊天式API接口
        :param api_key: API密钥
        :param base_url: API地址
        :param query: 查询内容
        :param model: 模型名称
        :return: 返回结果
        """
        request = GenericResponseGetter._chat_request(
            query=query, model=model, messages=messages, max_tokens=max_tokens
        )
        async with AsyncOpenAI(api_key=api_key, base_url=base_url) as async_client:
            completion = await async_client.chat.completions.create(**request)
        return completion.choices[0].message.content

    @staticmethod
    async def stream_response(
        api_key: str,
        base_url: str,
        query: str = '',
        model: str = 'deepseek-v3-250324',
        messages: list[dict[str, str]] | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ):
        request = GenericResponseGetter._chat_request(
            query=query, model=model, messages=messages, max_tokens=max_tokens
        )
        async with AsyncOpenAI(api_key=api_key, base_url=base_url) as async_client:
            stream = await async_client.chat.completions.create(**request, stream=True)
            async for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    @staticmethod
    async def get_vector(
        query: str,
        model: str = 'text-embedding-3-small',
        api_key: str = '',
        base_url: str = '',
    ) -> list[float]:
        """
        向量嵌入API接口
        :param query: 查询内容
        :param model: 模型名称
        :param api_key: API密钥
        :param base_url: API地址
        """

        # 初始化异步Embedding客户端
        async with AsyncOpenAI(api_key=api_key, base_url=base_url) as async_embedding_client:
            completion = await async_embedding_client.embeddings.create(model=model, input=[query])
        return completion.data[0].embedding


class ResponseGetterFactory:
    @staticmethod
    def create() -> GenericResponseGetter:
        # 替换使用模型
        return GenericResponseGetter()
