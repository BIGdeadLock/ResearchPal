from typing import Generator

import tiktoken
from loguru import logger
from transformers import AutoTokenizer

from llm_engineering.settings import settings


def flatten(nested_list: list) -> list:
    """Flatten a list of lists into a single list."""

    return [item for sublist in nested_list for item in sublist]


def batch(list_: list, size: int) -> Generator[list, None, None]:
    yield from (list_[i : i + size] for i in range(0, len(list_), size))


def compute_num_tokens(text: str) -> int:
    tokenizer = AutoTokenizer.from_pretrained(settings.HF_MODEL_ID)

    return len(tokenizer.encode(text, add_special_tokens=False))


def get_num_tokens(text: str, model_name="cl100k_base") -> int:
    """
    Counts the number of tokens in a string using a specified encoding.

    Args:
        text (str): The input string.
        model_name (str): The encoding model to use. Defaults to "cl100k_base" (used by GPT-4 and newer models).

    Returns:
        int: The number of tokens in the string.
    """
    try:
        encoding = tiktoken.get_encoding(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except KeyError:
        logger.error(
            f"Error: Encoding model '{model_name}' not found. Using default 'cl100k_base' which is used by most recent models."
        )
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 0
