from zenml import pipeline

from steps.etl import collect_documents, get_or_create_user


@pipeline
def digital_data_etl(user_full_name: str, interested: list[str], platforms: list[str]) -> str:
    user_full_name = get_or_create_user(user_full_name)
    last_step = collect_documents(user=user_full_name, field_of_interest=interested, platforms=platforms)
    return last_step.invocation_id
