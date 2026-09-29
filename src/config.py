"""Central configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    safe_browsing_key: str = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
    virustotal_key: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_store")
    max_retrieval_rounds: int = int(os.getenv("MAX_RETRIEVAL_ROUNDS", "2"))
    embedding_model: str = "all-MiniLM-L6-v2"


settings = Settings()
