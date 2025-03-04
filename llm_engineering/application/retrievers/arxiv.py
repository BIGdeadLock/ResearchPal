from arxiv import Client, Search
from loguru import logger

from llm_engineering.domain.documents import ArxivPaperDocument

from .base import BaseRetriever
from .constants import DEFAULT_TOP_K_PAPERS, TOP_K_PAPERS_TOKEN


class ArxivRetriever(BaseRetriever):
    model = ArxivPaperDocument

    def __init__(self) -> None:
        super().__init__()

    def extract(self, query: str, **kwargs) -> None:
        top_k_papers = kwargs.get(TOP_K_PAPERS_TOKEN, DEFAULT_TOP_K_PAPERS)

        logger.info(f"Starting retrieving papers for query: {query}")

        search = Search(
            query=query,
            max_results=top_k_papers,
        )

        for paper in Client().results(search):
            instance = self.model(
                content=paper.summary,
                title=paper.title,
                release_date=paper.published.strftime("%Y-%M-%d"),
                url=paper.pdf_url,
                journal=paper.journal_ref,
                categories=paper.categories,
            )

            instance.save()

        logger.info(f"Finished retrieving {top_k_papers} papers")
