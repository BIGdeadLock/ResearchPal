from typing import Optional

from pydantic import UUID4, BaseModel, Field

from llm_engineering.domain.base import VectorBaseDocument
from llm_engineering.domain.types import DataCategory


class Query(VectorBaseDocument):
    content: str
    author_id: UUID4 | None = None
    author_full_name: str | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        category = DataCategory.QUERIES

    @classmethod
    def from_str(cls, query: str) -> "Query":
        return Query(content=query.strip("\n "))

    def replace_content(self, new_content: str) -> "Query":
        return Query(
            id=self.id,
            content=new_content,
            author_id=self.author_id,
            author_full_name=self.author_full_name,
            metadata=self.metadata,
        )


class EmbeddedQuery(Query):
    embedding: list[float]

    class Config:
        category = DataCategory.QUERIES


class PaperQuery(BaseModel):
    source: str = Field(description="Data source to fetch the papers from", default="arxiv")
    query: str = Field(description="The query to look papers for")
    release_date_filter: Optional[str] = Field(
        description="Filter all papers released before this date. Date format: %Y-%m-%d", default=None
    )
