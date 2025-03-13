from gitingest import ingest
from loguru import logger
from tavily import TavilyClient

from llm_engineering.application.utils.misc import get_num_tokens
from llm_engineering.domain.documents import RepositoryDocument
from llm_engineering.domain.queries import CollectorQuery
from llm_engineering.model.api.gemini import Gemini
from llm_engineering.settings import settings

from .base import BaseCollector
from .constants import MAX_RESULTS, MAX_TOKENS_ALLOWED


class GithubCollector(BaseCollector):
    model = RepositoryDocument
    platform = "github"

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png"), mock=False) -> None:
        super().__init__()
        self._ignore = ignore
        self._mock = mock

    def collect(self, query: CollectorQuery, **kwargs) -> None:
        logger.info(f"Searching online for github repositories that matches the query: {query}")
        if kwargs.get("mock", False):
            result = {
                "results": [
                    {
                        "content": "612 stars 60 forks Branches Tags Activity Assessing Cybersecurity Vulnerabilities in Code Large Language Models | arXiv | 202...Paper Link Generative AI and Large Language Models for Cyber Security: All Insights You Need | arXiv | 2024.05.21 | Paper Link",
                        "raw_content": None,
                        "score": 0.5689194,
                        "title": "When LLMs Meet Cybersecurity: A Systematic Literature Review - GitHub",
                        "url": "https://github.com/tmylla/Awesome-LLM4Cybersecurity",
                    },
                    {
                        "content": "Borrowing a concept from the cybersecurity world, we believe that to truly mitigate the challenges which generative AI presen...ties, is a collaborative approach to evaluating and mitigating potential risks and the same ethos applies to generative AI and",
                        "raw_content": None,
                        "score": 0.5027105,
                        "title": "GitHub - meta-llama/PurpleLlama: Set of tools to assess and improve LLM ...",
                        "url": "https://github.com/meta-llama/PurpleLlama",
                    },
                    {
                        "content": "Awesome Large Language Model Tools for Cybersecurity Research Reverse Engineering G-3PO: A Protocol Droid for Ghidra : An AI ...er at Tenable for analysing and annotating decompiled code in Ghidra, which queries OpenAI and/or Anthropic's language models.",
                        "raw_content": None,
                        "score": 0.49040702,
                        "title": "GitHub - tenable/awesome-llm-cybersecurity-tools: A curated list of ...",
                        "url": "https://github.com/tenable/awesome-llm-cybersecurity-tools",
                    },
                ]
            }
        else:
            result = TavilyClient(api_key=settings.TAVILY_API_KEY).search(query.content, max_results=MAX_RESULTS)

        documents = result["results"]

        for document in documents:
            link = document["url"]

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
                readme = Gemini().generate(query=f"Create a concise summary for the following: {readme}")

            user = kwargs["user"]
            instance = self.model(
                content=readme,
                link=link,
                platform="github",
                requester_id=user.id,
                requester_full_name=user.full_name,
            )
            instance.save()

            logger.info(f"Finished scrapping GitHub repository: {link}")
