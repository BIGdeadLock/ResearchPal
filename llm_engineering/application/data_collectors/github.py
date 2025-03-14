from gitingest import ingest
from loguru import logger

from llm_engineering.application.utils.misc import get_num_tokens
from llm_engineering.domain.documents import RepositoryDocument
from llm_engineering.domain.queries import CollectorQuery
from llm_engineering.model.api.gemini import Gemini

from .base import BaseCollector
from .constants import MAX_TOKENS_ALLOWED, TAVILIY_GITHUB_MOCK_RESULTS
from .web import TaviliyAdapter


class GithubCollector(BaseCollector):
    model = RepositoryDocument
    platform = "github"

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png"), mock=False) -> None:
        super().__init__()
        self._ignore = ignore
        self._mock = mock

    def collect(self, query: CollectorQuery, **kwargs) -> None:
        logger.info(f"Searching online for github repositories that matches the query: {query.content}")
        if kwargs.get("mock", False):
            documents = TAVILIY_GITHUB_MOCK_RESULTS
        else:
            documents = TaviliyAdapter().search(query.content)

        for document in documents:
            link = document.link

            if "github" not in link:
                logger.warning(f"Found non github link: {link}, Skipping")
                continue

            old_model = self.model.find(link=link)
            if old_model is not None:
                logger.info(f"Repository already exists in the database: {link}")

                return

            logger.info(f"Starting scrapping GitHub repository: {link}")

            # Ingest only the readme file which will contain a summary for the repo
            summary, tree, content = ingest(link, include_patterns="*.md")
            readme = content.replace("=", "").replace("\n", " ").strip()

            # Create a small summary for the readme if it is above 500 tokens
            if get_num_tokens(readme) > MAX_TOKENS_ALLOWED:
                logger.warning(
                    f"Github README has {get_num_tokens(readme)}," f" summarizing it to {MAX_TOKENS_ALLOWED} tokens"
                )
                readme = Gemini().generate(query=f"Create a concise summary for the following: {readme}")

            user = kwargs["user"]
            instance = self.model(
                content=readme,
                link=link,
                platform="github",
                requester_id=user.id,
                requester_full_name=user.full_name,
                title=link.split("/")[-1],
            )

            # if instance.find(link=link) is not None:
            instance.save()
            # else:
            #     logger.info(f"Repo {link} is already in the database")

            logger.info(f"Finished scrapping GitHub repository: {link}")
