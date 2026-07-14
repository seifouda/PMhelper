"""
Server Configuration

Manages environment variables and configuration for different environments.
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""

    def __init__(self):
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        # Database URL - auto-detects PostgreSQL or SQLite
        self._database_url = os.getenv("DATABASE_URL")

        # CORS origins
        self.CORS_ORIGINS = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:4200,http://localhost:8000"
        ).split(",")

        # Render.com specific
        self.IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
        self.PORT = int(os.getenv("PORT", "8000"))

        # Server settings (for backward compatibility with old api/main.py)
        self.HOST = os.getenv("PMHELPER_HOST", "127.0.0.1")
        self.LOG_LEVEL = os.getenv("PMHELPER_LOG_LEVEL", "INFO")

    def get_database_url(self) -> str:
        """
        Get database URL for current environment.

        Returns:
            Database URL for PostgreSQL (production) or SQLite (local)
        """
        if self._database_url:
            # Render.com provides DATABASE_URL
            # Fix: Render uses 'postgres://' but SQLAlchemy needs
            # 'postgresql://'
            if self._database_url.startswith("postgres://"):
                return self._database_url.replace(
                    "postgres://", "postgresql+asyncpg://", 1)
            return self._database_url

        # Local development: Use SQLite
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "pmhelper.db"
        return f"sqlite+aiosqlite:///{db_path}"

    def get_server_url(self) -> str:
        """Get the complete server URL."""
        host = "localhost" if self.HOST == "127.0.0.1" else self.HOST
        return f"http://{host}:{self.PORT}"

    def get_docs_url(self) -> str:
        """Get the API documentation URL."""
        return f"{self.get_server_url()}/docs"

    def is_network_mode(self) -> bool:
        """Check if server is configured for network access."""
        return self.HOST == "0.0.0.0"


config = Config()
