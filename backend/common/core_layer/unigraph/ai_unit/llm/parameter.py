# ----------------------------所有LLM的参数配置类皆在此处
import random
from typing import List


class DEEPSEEK_API_PARAMETER:
    def __init__(self, deepseek_api_key_list: List = None, base_url: str = 'https://ark.cn-beijing.volces.com/api/v3'):
        self.deepseek_api_key_list = deepseek_api_key_list
        self.base_url = base_url

    @property
    def deepseek_api_key(self):
        random.shuffle(self.deepseek_api_key_list)
        return self.deepseek_api_key_list[0]
