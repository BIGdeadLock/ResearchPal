from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm_engineering.application.retrievers.dispatcher import RetrieverDispatcher
from llm_engineering.domain.documents import UserDocument


@step
def fetch_papers(user: UserDocument, queries: list[dict]) -> Annotated[list[str], "queries"]:
    dispatcher = RetrieverDispatcher.build().register_arxiv()

    logger.info(f"Starting to retrieve papers for {len(queries)} queries.")

    metadata = {}
    successfull_retrieves = 0
    questions = []
    for source_query in tqdm(queries):
        source, query = source_query.popitem()
        questions.append(query)
        successfull_ret = _retrieve_papers(dispatcher, source, query, user)
        successfull_retrieves += successfull_ret

        metadata = _add_to_metadata(metadata, source, successfull_ret)

    step_context = get_step_context()
    step_context.add_output_metadata(output_name="fetch_papers", metadata=metadata)

    logger.info(f"Successfully retrieved {successfull_retrieves} / {len(queries)} queries.")

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
