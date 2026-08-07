from ...unigraph.web_search.search_engine.web_search_api import SearchContext
from .scrapy_engine.spider_clearner import SpiderContentCleaner
from .search_engine.web_search_api import SpiderSearch


class SearchAndScrapePipeLine:
    def __init__(self):
        self.search_context = SearchContext(SpiderSearch())  # the key is from config.py

    async def run(self, keyword) -> list:
        """
        Run the search and scrape pipeline.
        :param keyword: The infer triple to search.
        :return: The search result
        """
        # get triple related links
        search_result = await self.search_context.perform_search(keyword)
        # 确保网络来源与链接被利用 注意一个url又多个来源，需要甄别。
        search_content_list = [
            {'content': '\n'.join(SpiderContentCleaner.clean(each_result['content'])), 'url': each_result['url']}
            for each_result in search_result
        ]
        return search_content_list
