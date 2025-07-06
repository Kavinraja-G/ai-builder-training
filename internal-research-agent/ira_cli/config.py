"""
Configuration management for the Internal Research Agent.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

    # Model Configuration
    model_name: str = Field(default="gemini-2.0-flash", env="MODEL_NAME")
    temperature: float = Field(default=0.0, env="TEMPERATURE")
    max_retries: int = Field(default=2, env="MAX_RETRIES")

    # Document Processing
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")
    docs_path: str = Field(default="hr_docs", env="DOCS_PATH")

    # Vector Store
    vector_store_path: str = Field(default="./chroma_db", env="VECTOR_STORE_PATH")

    # Search Configuration
    max_search_results: int = Field(default=5, env="MAX_SEARCH_RESULTS")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()