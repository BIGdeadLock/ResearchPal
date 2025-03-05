from zenml import pipeline

from llm_engineering.domain.queries import PaperQuery
from steps.etl import crawl_links, fetch_papers, get_or_create_user


@pipeline
def digital_data_etl(user_full_name: str, links: list[str]) -> str:
    user = get_or_create_user(user_full_name)
    last_step = crawl_links(user=user, links=links)
    return last_step.invocation_id


@pipeline
def papers_digital_data_etl(user_full_name: str, papers: list[dict]) -> str:
    user_full_name = get_or_create_user(user_full_name)
    papers = [PaperQuery(source=p["source"], query=p["query"]) for p in papers]
    last_step = fetch_papers(user=user_full_name, papers_queries=papers)
    return last_step.invocation_id
