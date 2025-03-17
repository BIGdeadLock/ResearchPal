from loguru import logger

from llm_engineering import settings
from llm_engineering.domain.documents import PaperDocument, RepositoryDocument
from llm_engineering.infrastructure.db.mongo import connection

_database = connection.get_database(settings.DATABASE_NAME)


def update_feedback(feedback: int, link: str, platform: str) -> bool:
    try:
        if platform == "github":
            document = RepositoryDocument.find(link=link)

        elif platform == "arxiv":
            document = PaperDocument.find(link=link)

        else:
            logger.info(f"Could not a record with {link}. Aborting")
            return False

        logger.info(f"Found a document that matches {link}")
        if document.update_field("user_feedback", feedback):
            logger.info("Successfully updated user feedback")
            return True
        else:
            logger.info("Failed to update user feedback")
            return False

    except Exception as e:
        logger.error(e)
        raise e
