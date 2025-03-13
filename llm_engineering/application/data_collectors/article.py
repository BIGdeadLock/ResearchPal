from llm_engineering.domain.documents import ArticleDocument

from .base import BaseCollector


class ArticleCollector(BaseCollector):
    model = ArticleDocument

    def collect(self, link: str, **kwargs) -> None:
        pass
