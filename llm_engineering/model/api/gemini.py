from google import genai

from llm_engineering.settings import settings


class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate(self, query: str, schema=None):
        args = dict(
            model=settings.GEMINI_MODEL_ID,
            contents=query,
        )
        if schema:
            args = args | dict(config=dict(response_mime_type="application/json", response_schema=schema))

        response = self.client.models.generate_content(**args)

        if not schema:
            return response.text

        else:
            return response.parsed
