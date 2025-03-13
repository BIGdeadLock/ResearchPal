from zenml import pipeline

from steps.etl import collect_documents, crawl_links, get_or_create_user


@pipeline
def digital_data_etl(user_full_name: str, links: list[str]) -> str:
    user = get_or_create_user(user_full_name)
    last_step = crawl_links(user=user, links=links)
    return last_step.invocation_id


@pipeline
def data_collection(user_full_name: str, fields: list[str], platforms: list[str]) -> str:
    user_full_name = get_or_create_user(user_full_name)
    last_step = collect_documents(user=user_full_name, field_of_interest=fields, platforms=platforms)
    return last_step.invocation_id
