import asyncio
import os
from typing import Dict, List

import numpy as np

from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter


async def batch_get_vectors(words: List[str]) -> Dict[str, List[float]]:
    """
    批量获取词向量（改为逐个调用 get_vector 实现）

    参数:
        words: 需要获取嵌入向量的单词/短语列表
        model: 使用的嵌入模型名称（默认从 settings 读取）

    返回:
        字典形式返回每个单词对应的嵌入向量
    """
    # 为每个单词创建获取向量的异步任务
    tasks = [
        GenericResponseGetter.get_vector(
            query=word, api_key=os.getenv('OPENAI_API_KEY', ''), base_url='https://api.rcouyi.com/v1'
        )
        for word in words
    ]

    # 并发执行所有任务
    embeddings = await asyncio.gather(*tasks)

    # 将单词和对应向量组合成字典
    return dict(zip(words, embeddings))


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculate the cosine similarity between two vectors.

    Cosine similarity measures the angle between two vectors, ranging from -1 (opposite)
    to 1 (identical), with 0 indicating orthogonality.

    Args:
        vector_a: First vector for comparison
        vector_b: Second vector for comparison

    Returns:
        Cosine similarity value between -1.0 and 1.0

    Raises:
        ValueError: If vectors have different lengths or are zero vectors
    """
    # Convert input lists to numpy arrays for numerical operations
    a = np.array(vector_a, dtype=float)
    b = np.array(vector_b, dtype=float)

    # Validate input vectors
    if len(a) != len(b):
        raise ValueError('Vectors must have the same length')
    if not np.any(a) or not np.any(b):
        raise ValueError('Zero vectors are not allowed')

    # Calculate dot product and vector norms
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Compute and clamp the cosine similarity to ensure valid range
    return np.clip(dot_product / (norm_a * norm_b), -1.0, 1.0)
