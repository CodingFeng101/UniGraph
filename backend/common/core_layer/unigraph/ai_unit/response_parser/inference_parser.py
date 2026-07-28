from typing import List, Tuple

from .base_parser import ResponseParser
from .extraction_parser import AttributeExtractionResponseParser


class MaskedTripleInferenceResponseParser(ResponseParser):
    @staticmethod
    def parse(response: str, **kwargs) -> Tuple[List[Tuple[str, str, str]], List[str]]:
        """
        解析关系三元组提取的字符串
        :param response: 关系三元组提取的字符串 -> (e1, r1, e2) && (e3, r2, e4) && ...
        :return: 解析后的三元组列表 -> [(e1, r1, e2), (e3, r2, e4), ...]
                 实体列表 -> [e1, e2, ...]
        """
        # 去除不规则的空白字符和换行符
        cleaned_string = response.replace('\n', '').replace('\t', '')
        # 拆分整个字符串为以 "&&" 分隔的条目
        entries = [entry.strip() for entry in cleaned_string.split('&&') if entry.strip()]

        triples = []
        extracted_entities = []

        # 迭代每一个条目并拆分为三元组
        for entry in entries:
            try:
                # 去除两侧括号并按照逗号分隔
                elements = entry.strip('()').split(',')

                # 验证是否为有效的三元组
                if len(elements) == 3:
                    e1, r, e2 = elements[0].strip(), elements[1].strip(), elements[2].strip()
                    triples.append((e1, r, e2))
                    # 将提取得实体添加进列表
                    extracted_entities.extend([e1, e2])
            except Exception:
                pass

        return triples, list(set(extracted_entities))


class InferredEntityAttributeInferenceResponseParser(ResponseParser):
    @staticmethod
    def parse(response: str, **kwargs) -> dict:
        """
        解析实体属性推理的字符串
        :param response: 以分号分隔的实体属性字符串。
        :return: 解析后的实体字典 -> {e1: {attr1: value1, attr2: value2}, e2: {attr1: value1, attr2: value2}, ...}
        """
        return AttributeExtractionResponseParser.parse(response)
