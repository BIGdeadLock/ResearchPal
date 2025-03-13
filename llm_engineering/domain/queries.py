from pydantic import UUID4, BaseModel, Field

from llm_engineering.domain.base import VectorBaseDocument
from llm_engineering.domain.types import DataCategory


class Query(VectorBaseDocument):
    content: str
    requester_id: UUID4 | None = None
    requester_full_name: str | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        category = DataCategory.QUERIES

    @classmethod
    def from_str(cls, query: str) -> "Query":
        return Query(content=query.strip("\n "))

    @classmethod
    def from_list(cls, keywords: list[str]) -> "Query":
        return Query(content=", ".join(keywords))

    def replace_content(self, new_content: str) -> "Query":
        return Query(
            id=self.id,
            content=new_content,
            requester_id=self.author_id,
            requester_full_name=self.author_full_name,
            metadata=self.metadata,
            platform=self.platform,  # Preserve the platform
        )


class EmbeddedQuery(Query):
    embedding: list[float]

    class Config:
        category = DataCategory.QUERIES


class CollectorQuery(BaseModel):
    content: str
    platform: str | None = None

    def replace_content(self, new_content: str) -> "CollectorQuery":
        return CollectorQuery(content=new_content, platform=self.platform)
