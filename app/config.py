import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "travel-chatbot")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "ragplan-travel")
    PINECONE_NAMESPACE: str = os.getenv("PINECONE_NAMESPACE", "travel-guides")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
    PINECONE_EMBEDDING_MODEL: str = os.getenv("PINECONE_EMBEDDING_MODEL", "text-embedding-3-small")

settings = Settings()

if settings.LANGSMITH_API_KEY:
    # Support both newer LANGSMITH_* and legacy LANGCHAIN_* env names.
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
    os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGSMITH_TRACING_V2"] = "true"

    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
else:
    # Avoid noisy auth errors when key is not configured.
    os.environ["LANGSMITH_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
