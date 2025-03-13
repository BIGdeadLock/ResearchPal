from abc import ABC, abstractmethod

from llm_engineering.domain.documents import NoSQLBaseDocument
from llm_engineering.domain.queries import CollectorQuery


class BaseCollector(ABC):
    model: type[NoSQLBaseDocument]
    platform: str

    @abstractmethod
    def collect(self, query: CollectorQuery, **kwargs) -> None: ...
