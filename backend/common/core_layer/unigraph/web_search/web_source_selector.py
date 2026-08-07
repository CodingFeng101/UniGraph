import json
import os
import re
from typing import List, Tuple

# 手动设置 HOME 环境变量
# os.environ["HOME"] = "C:/Users/Lenovo"
# # 手动设置 Path.home() 方法的返回值
# Path.home = lambda: Path(os.environ["HOME"])
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()


class WebSourceSelector:
    @staticmethod
    def mixed_language_sentence_segmenter(text):
        """
        处理混合语言的文本，使用标点符号进行句子分割。
        Args:
            text (str): 输入文本，可能包含中英、法德混合句子。
        Returns:
            List[str]: 分句后的句子列表。
        """
        # 匹配常见的中英法德标点符号，作为句子分割的依据
        sentence_endings = re.compile(r'(?<=[.!?！？。])\s*')
        sentences = sentence_endings.split(text)
        # 过滤掉空白句子，并去掉首尾多余空格
        return [sent.strip() for sent in sentences if len(sent.strip()) > 0]

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本中的无关符号，仅保留基础标点符号和中文常用符号。
        允许的字符包括中文、英文字母、数字及部分基础标点（如句号、逗号等）。

        参数:
        text (str): 待清理的文本

        返回:
        str: 清理后的纯净文本
        """
        # 保留的字符: 中文、字母、数字、逗号、句号、感叹号、问号等
        cleaned_text = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5，。,！？；：、]', '', text)
        return cleaned_text

    @staticmethod
    def select_sentences(web_content: List, triple: Tuple) -> List:
        """
        根据输入的网页内容和三元组，查找与三元组最相关的句子。

        参数：
        web_content (List[str]): 处理后的网页文本内容，按段落或句子分割的列表
        triple (Tuple[str, str, str]): 三元组 (实体1, 关系, 实体2)
        top_k (int): 返回最相关的前k个句子
        threshold (float): 过滤阈值，返回相似度大于该阈值的句子

        返回：
        List[Tuple[str, float]]: 按照相似度排序的相关句子及其分数
        """
        e1, r1, e2 = triple
        triple_str = f'{e1} {r1} {e2}'
        cleaned_web_content = [
            {'content': WebSourceSelector.clean_text(sentence['content']), 'url': sentence['url']}
            for sentence in web_content
        ]
        if not cleaned_web_content:
            return []

        texts = [json.dumps(chunk, ensure_ascii=False) for chunk in cleaned_web_content]
        embeddings = OpenAIEmbeddings(model=os.getenv('EMBEDDING_MODEL'))
        document_vectors = np.asarray(embeddings.embed_documents(texts), dtype=float)
        query_vector = np.asarray(embeddings.embed_query(triple_str), dtype=float)
        norms = np.linalg.norm(document_vectors, axis=1) * np.linalg.norm(query_vector)
        scores = np.divide(
            document_vectors @ query_vector,
            norms,
            out=np.full(len(document_vectors), -1.0),
            where=norms != 0,
        )
        related_source = [cleaned_web_content[index] for index in np.argsort(scores)[-2:][::-1]]

        # check if repeat
        if len(related_source) == 2:
            if related_source[0] == related_source[1]:
                return []  # 可能由多个链接，前端需要展示至少两个链接。如果一致则返回空列表，策略认为没有合适的来源

        return related_source
