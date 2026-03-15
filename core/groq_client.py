import os
from groq import Groq
from utils.config import config
from utils.logger import Logger

class GroqClient:
    def __init__(self):
        if not config.groq_api_key:
            Logger.error("GROQ_API_KEY not found in .env file")
            self.client = None
        else:
            self.client = Groq(api_key=config.groq_api_key)

    def chat(self, prompt, system_prompt="You are an expert Red Team security researcher."):
        if not self.client:
            return "Error: Groq client not initialized."

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=config.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            Logger.error(f"Groq API Error: {str(e)}")
            return f"Error: {str(e)}"

groq_client = GroqClient()
