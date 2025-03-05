from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm_engineering.application.retrievers.dispatcher import RetrieverDispatcher
from llm_engineering.domain.documents import UserDocument
from llm_engineering.domain.queries import PaperQuery


@step
def fetch_papers(user: UserDocument, papers_queries: list[PaperQuery]) -> Annotated[list[str], "queries"]:
    dispatcher = RetrieverDispatcher.build().register_arxiv()

    logger.info(f"Starting to retrieve papers for {len(papers_queries)} queries.")

    metadata = {}
    successfull_retrieves = 0
    questions = []
    for paper_query in tqdm(papers_queries):
        questions.append(paper_query.query)
        successfull_ret = _retrieve_papers(dispatcher, paper_query.source, paper_query.query, user)
        successfull_retrieves += successfull_ret

        metadata = _add_to_metadata(metadata, paper_query.source, successfull_ret)

    step_context = get_step_context()
    step_context.add_output_metadata(output_name="queries", metadata=metadata)

    logger.info(f"Successfully retrieved papers for {successfull_retrieves} / {len(papers_queries)} queries.")

    return questions


def _retrieve_papers(dispatcher: RetrieverDispatcher, source: str, query: str, user: UserDocument) -> bool:
    retriever = dispatcher.get_retriever(source)

    try:
        retriever.extract(query=query, user=user)

        return True
    except Exception as e:
        logger.error(f"An error occurred while retrieving: {e!s}")

        return False


def _add_to_metadata(metadata: dict, source: str, successfull_ret: bool) -> dict:
    if source not in metadata:
        metadata[source] = {}
    metadata[source]["successful"] = metadata.get(source, {}).get("successful", 0) + successfull_ret
    metadata[source]["total"] = metadata.get(source, {}).get("total", 0) + 1

    return metadata
