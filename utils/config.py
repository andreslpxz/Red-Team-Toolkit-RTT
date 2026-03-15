import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.log_path = "logs/aura.log"
        self.db_path = "data/db/aura.db"

    def is_valid(self):
        return bool(self.groq_api_key)

config = Config()
