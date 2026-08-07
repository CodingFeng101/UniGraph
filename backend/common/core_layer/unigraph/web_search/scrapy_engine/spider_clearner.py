import re

import markdown2
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md
from sklearn.feature_extraction.text import TfidfVectorizer


class SpiderContentCleaner:
    @staticmethod
    def clean(scraped_data: str):
        markdown_content = SpiderContentCleaner.convert_html_to_markdown(scraped_data)
        cleaned_md_content = SpiderContentCleaner.clean_md_content(markdown_content)
        paragraphs = SpiderContentCleaner.split_md_into_paragraphs(cleaned_md_content)
        if not paragraphs:
            return []
        important_paragraphs = SpiderContentCleaner.extract_important_paragraphs(paragraphs)

        return important_paragraphs

    @staticmethod
    def clean_md_content(md_content: str):
        # 将md内容转为HTML再转为纯文本
        html_content = markdown2.markdown(md_content)
        # 移除图片标签
        html_content = re.sub(r'!\[.*?\]\(.*?\)', '', html_content)
        # 移除链接标签
        html_content = re.sub(r'\[.*?\]\(.*?\)', '', html_content)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', html_content)

        return text

    @staticmethod
    def split_md_into_paragraphs(md_content):
        # 移除多余的换行符，确保段落之间的空行被保留
        md_content = re.sub(r'\n{2,}', '\n\n', md_content)
        # 将md文档按照两个换行符进行分割，以形成段落
        paragraphs = md_content.split('\n\n')
        # 移除每个段落前后的多余空白符
        paragraphs = [paragraph.strip() for paragraph in paragraphs]
        # 过滤掉空段落
        paragraphs = [paragraph for paragraph in paragraphs if paragraph]
        return paragraphs

    @staticmethod
    def preprocess_text(paragraph: str) -> str:
        """
        预处理段落文本，去除连续重复的符号、无意义的字符串等噪声。

        参数：
        paragraph (str): 原始段落文本

        返回：
        str: 经过预处理后的段落文本
        """
        # 定义重复字符或符号的正则表达式模式（例如: ********, //////, \n\n\n）
        noise_patterns = [
            r'(\*+)',  # 匹配连续的 * 号
            r'(\/+)',  # 匹配连续的 / 号
            r'(-+)',  # 匹配连续的 - 号
            r'(_+)',  # 匹配连续的 _ 号
            r'(\n+)',  # 匹配连续的换行符
            r'(\s{2,})',  # 匹配连续多个空格
        ]

        # 依次去除所有定义的噪声模式
        for pattern in noise_patterns:
            paragraph = re.sub(pattern, ' ', paragraph)

        # 去除多余空白并返回
        return paragraph.strip()

    @staticmethod
    def extract_important_paragraphs(paragraphs):
        """
        使用TF-IDF对网页段落进行重要性排序，并提取前3个最重要段落。

        参数：
        paragraphs (List[str]): 待处理的段落列表

        返回：
        List[str]: 经过排序的前3个重要段落
        """
        # 1. 先对段落列表中的每个段落进行预处理
        cleaned_paragraphs = [SpiderContentCleaner.preprocess_text(paragraph) for paragraph in paragraphs]

        # 2. 使用TF-IDF计算段落重要性分数
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(cleaned_paragraphs)

        # 3. 计算每个段落的重要性得分（TF-IDF值的总和）
        importance_scores = X.sum(axis=1).A1

        # 4. 依托重要性得分对段落进行排序
        sorted_paragraphs = [
            paragraph for score, paragraph in sorted(zip(importance_scores, cleaned_paragraphs), reverse=True)
        ]

        # 5. 返回排序后的前3个重要段落
        return sorted_paragraphs[:3]

    @staticmethod
    def clean_html_content(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # 移除所有<style>和<script>标签及其内容
        for element in soup(['style', 'script', 'head', 'meta', 'link']):
            element.decompose()
        # 移除所有<a>标签，但保留其中的文本内容
        for a in soup.find_all('a'):
            a.unwrap()
        # 移除所有注释内容
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        # 获取干净的HTML内容
        cleaned_html = str(soup)
        return cleaned_html

    @staticmethod
    def convert_html_to_markdown(html_content):
        # 清理HTML内容
        cleaned_html_content = SpiderContentCleaner.clean_html_content(html_content)
        # 替换HTML中的&nbsp;为普通空格
        cleaned_html_content = cleaned_html_content.replace('\xa0', ' ').replace('&nbsp;', ' ')
        # 转换为Markdown
        markdown_content = md(cleaned_html_content)
        # 去除多余空行
        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
        # 去除Markdown中的代码块
        markdown_content = re.sub(r'```.*?```', '', markdown_content, flags=re.DOTALL)
        return markdown_content
