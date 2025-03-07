import opik
import pydantic
from loguru import logger

from llm_engineering.application.rag.base import RAGStep
from llm_engineering.application.rag.prompt_templates import QueryBuilderPromptTemplate
from llm_engineering.domain.queries import Query
from llm_engineering.model.api.gemini import Gemini


class Queries(pydantic.BaseModel):
    queries: list[str] = pydantic.Field(description="List of generated queries from keywords")


class QueryBuilder(RAGStep):
    @opik.track(name="QueryBuilder.generate")
    def generate(self, query: Query, number_of_queries: int) -> list[Query]:
        assert number_of_queries > 0, f"'number_of_queries' should be greater than 0. Got {number_of_queries}."

        if self._mock:
            return [query for _ in range("LLM agents in cybersecurity")]

        query_expansion_template = QueryBuilderPromptTemplate()
        prompt = query_expansion_template.get_str_prompt(fields=query.content, number_of_queries=number_of_queries)

        queries_content = Gemini().generate(query=prompt, schema=Queries)
        queries = [Query.from_str(content) for content in queries_content.queries]

        return queries


if __name__ == "__main__":
    query = Query.from_list(["LLM", "Agents", "Cybersecurity"])
    query_builder = QueryBuilder()
    queries = query_builder.generate(query, number_of_queries=3)
    for query in queries:
        logger.info(query.content)
