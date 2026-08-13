from openai import OpenAI
from dotenv import load_dotenv
import os
import json


class LLMClient:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set."
            )

        with open("config/setting.json", "r", encoding="utf-8") as f:
            settings = json.load(f)

        self.model = settings["llm"]["model"]

        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text