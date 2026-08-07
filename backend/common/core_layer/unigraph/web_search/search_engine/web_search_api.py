import os
from abc import ABC, abstractmethod
from typing import List

import aiohttp
from dotenv import load_dotenv

load_dotenv()


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, keyword: str) -> str:
        pass


class SpiderSearch(SearchStrategy):
    def __init__(self):
        self.headers = {'Authorization': os.getenv('SPIDER_API_KEY'), 'Content-Type': 'application/json_data'}

    async def search(self, keyword: str) -> List:
        # get response from Spider API asynchronously
        query = {'search': keyword, 'search_limit': 3, 'limit': 1, 'return_format': 'markdown'}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.spider.cloud/search', headers=self.headers, json=query) as response:
                response_json = await response.json()  # load to content list
                return response_json


class SearchContext:
    def __init__(self, strategy: SearchStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy

    def perform_search(self, keyword: str):
        return self._strategy.search(keyword)
