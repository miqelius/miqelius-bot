import logging
from app.core.config import settings
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

        if self.provider == "gemini":
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        elif self.provider == "groq":
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def generate(self, prompt: str) -> str:
        try:
            if self.provider == "gemini":
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            elif self.provider == "groq":
                message = await self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                )
                return message.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise LLMError(f"Failed to generate response: {str(e)}")


llm_client = LLMClient()
