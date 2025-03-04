from abc import ABC, abstractmethod

from llm_engineering.domain.documents import NoSQLBaseDocument


class BaseRetriever(ABC):
    model: type[NoSQLBaseDocument]

    @abstractmethod
    def extract(self, query: str, **kwargs) -> None: ...
