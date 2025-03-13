from arxiv import Client, Search
from loguru import logger

from llm_engineering.domain.documents import PaperDocument, UserDocument
from llm_engineering.domain.queries import CollectorQuery

from .base import BaseCollector
from .constants import DEFAULT_TOP_K_PAPERS, TOP_K_PAPERS_TOKEN, USER_TOKEN


class ArxivCollector(BaseCollector):
    model = PaperDocument
    platform = "arxiv"

    def __init__(self) -> None:
        super().__init__()

    def collect(self, query: CollectorQuery, **kwargs) -> None:
        top_k_papers = kwargs.get(TOP_K_PAPERS_TOKEN, DEFAULT_TOP_K_PAPERS)
        user: UserDocument = kwargs[USER_TOKEN]
        logger.info(f"Starting retrieving papers for query: {query}")

        search = Search(
            query=query.content,
            max_results=top_k_papers,
        )

        for paper in Client().results(search):
            instance = self.model(
                content=paper.summary,
                title=paper.title,
                release_date=paper.published.strftime("%Y-%M-%d"),
                link=paper.pdf_url,
                platform="arxiv",
                requester_id=user.id,
                requester_full_name=user.full_name,
            )

            instance.save()

        logger.info(f"Finished retrieving {top_k_papers} papers")
