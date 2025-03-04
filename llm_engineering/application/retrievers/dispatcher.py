import re

from loguru import logger

from .arxiv import ArxivRetriever
from .base import BaseRetriever


class RetrieverDispatcher:
    def __init__(self) -> None:
        self._retrievers = {}

    @classmethod
    def build(cls) -> "RetrieverDispatcher":
        dispatcher = cls()

        return dispatcher

    def register_arxiv(self) -> "RetrieverDispatcher":
        self.register("arxiv", ArxivRetriever)

        return self

    def register(self, source: str, retriever: type[BaseRetriever]) -> None:
        self._retrievers[source] = retriever

    def get_retriever(self, source: str) -> BaseRetriever:
        for name, retriever in self._crawlers.items():
            if re.match(source, name):
                return retriever()
        else:
            logger.warning(f"No crawler found for {source}. Defaulting to ArxivRetriever.")

            return ArxivRetriever()
