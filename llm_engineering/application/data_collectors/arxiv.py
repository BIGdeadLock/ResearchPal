from arxiv import Client, Search
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
        logger.info(f"Starting retrieving papers for query: {query.content}")

        search = Search(
            query=query.content.strip(),
            max_results=settings.DATA_SOURCE_MAX_RESULTS,
        )

        count = 0
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

            # if instance.find(link=paper.pdf_url) is not None:
            instance.save()
            count += 1
            # else:
            #     logger.info(f"Paper {paper.title} is already in the database")

        logger.info(f"Finished retrieving {count} papers")
