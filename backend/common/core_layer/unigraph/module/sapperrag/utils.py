import json
from typing import Any, Dict, List


def parse_json(data: str, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将 JSON 数据解析为 Python 字典，并根据映射将键名进行转换。

    :param data: JSON 数据
    :param mapping: 键名映射，例如 {'old_key': 'new_key'}
    :return: 转换后的字典列表
    """
    return [
        {new_key: item.get(old_key, mapping[old_key]) for old_key, new_key in mapping.items()}
        for item in json.loads(data)
    ]


def num_tokens(text: str, token_encoder) -> int:
    """返回给定文本中的标记数"""
    return len(token_encoder.encode(text=text))
