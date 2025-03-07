from abc import ABC
from typing import Optional

from pydantic import UUID4, Field

from .base import NoSQLBaseDocument
from .types import DataCategory


class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    class Settings:
        name = "users"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Document(NoSQLBaseDocument, ABC):
    content: dict
    platform: str
    requester_id: UUID4 = Field(alias="requester_id")
    requester_full_name: str = Field(alias="requester_full_name")


class PaperDocument(Document):
    title: str
    release_date: str
    link: str
    content: str
    platform: str = "arxiv"
    kw: Optional[dict] = None

    class Settings:
        name = DataCategory.PAPERS


class RepositoryDocument(Document):
    name: str
    link: str

    class Settings:
        name = DataCategory.REPOSITORIES


class PostDocument(Document):
    image: Optional[str] = None
    link: str | None = None

    class Settings:
        name = DataCategory.POSTS


class ArticleDocument(Document):
    link: str
    kw: Optional[dict] = None

    class Settings:
        name = DataCategory.ARTICLES
