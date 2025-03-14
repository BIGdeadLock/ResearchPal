from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm_engineering.application.data_collectors.dispatcher import DataCollectorDispatcher
from llm_engineering.application.data_collectors.query_builder import QueryBuilder
from llm_engineering.domain.documents import UserDocument
from llm_engineering.domain.queries import CollectorQuery


@step
def collect_documents(
    user: UserDocument, field_of_interest: list[str], platforms: list[str]
) -> Annotated[list[str], "queries"]:
    dispatcher = DataCollectorDispatcher.build().register_arxiv()  # .register_github()

    logger.info(f"Starting to retrieve documents for {len(field_of_interest)} field of interest.")

    metadata = {}
    successfull_collections = 0
    questions = []
    for platform in tqdm(platforms):
        successfull_ret = _collect_document(dispatcher, field_of_interest, platform, user)
        successfull_collections += successfull_ret

        metadata = _add_to_metadata(metadata, platform, successfull_ret)

    step_context = get_step_context()
    step_context.add_output_metadata(output_name="queries", metadata=metadata)

    logger.info(
        f"Successfully retrieved documents for {successfull_collections} / "
        f"{dispatcher.number_of_collectors} collectors."
    )

    return questions


def _collect_document(
    dispatcher: DataCollectorDispatcher, fields: list[str], platform: str, user: UserDocument
) -> bool:
    collector = dispatcher.get_collector(platform)
    if collector is None:
        return False

    query_builder = QueryBuilder()
    query = CollectorQuery(content=str(fields), platform=platform)
    query = query_builder.generate(query)

    try:
        collector.collect(query=query, user=user)

        return True
    except Exception as e:
        logger.error(f"An error occurred while collecting using {collector.model} collector: {e!s}")

        return False


def _add_to_metadata(metadata: dict, source: str, successfull_ret: bool) -> dict:
    if source not in metadata:
        metadata[source] = {}
    metadata[source]["successful"] = metadata.get(source, {}).get("successful", 0) + successfull_ret
    metadata[source]["total"] = metadata.get(source, {}).get("total", 0) + 1

    return metadata


if __name__ == "__main__":
    field_of_interest = ["LLM", "Cybersecurity"]
    platforms = ["arxiv", "github"]
    user = UserDocument(first_name="Eden", last_name="Yavin")
    collect_documents(user, field_of_interest, platforms)
