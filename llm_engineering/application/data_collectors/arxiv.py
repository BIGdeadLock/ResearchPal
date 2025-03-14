from arxiv import Client, Search, SortCriterion
from loguru import logger

from llm_engineering.domain.documents import PaperDocument, UserDocument
from llm_engineering.domain.queries import CollectorQuery
from llm_engineering.settings import settings

from .base import BaseCollector
from .constants import USER_TOKEN


class ArxivCollector(BaseCollector):
    model = PaperDocument
    platform = "arxiv"

    def __init__(self, mock=False) -> None:
        super().__init__()
        self._mock = mock

    def collect(self, query: CollectorQuery, **kwargs) -> None:
        user: UserDocument = kwargs[USER_TOKEN]
        logger.info(f"Starting retrieving papers for query: {query}")

        search = Search(
            query=query.content, max_results=settings.DATA_SOURCE_MAX_RESULTS, sort_by=SortCriterion.SubmittedDate
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

        logger.info(f"Finished retrieving {settings.DATA_SOURCE_MAX_RESULTS} papers")
