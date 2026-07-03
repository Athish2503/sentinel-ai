import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Determine the base directory and load .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseModel):
    """
    App settings loaded from environment variables and validated with Pydantic.
    """
    # Handles potential typo in environment variables (DATBASE_URL vs DATABASE_URL)
    DATABASE_URL: str = Field(
        default_factory=lambda: (
            os.getenv("DATABASE_URL") or 
            os.getenv("DATBASE_URL") or 
            "postgresql://postgres:postgres@localhost:5432/postgres"
        )
    )
    GROQ_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    LOG_LEVEL: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    APP_NAME: str = Field(default="Sentinel AI")
    API_V1_STR: str = Field(default="/api/v1")

    @property
    def database_url_sqlalchemy(self) -> str:
        """
        SQLAlchemy requires 'postgresql://' instead of 'postgres://'.
        This helper normalizes the connection string prefix if needed.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()
