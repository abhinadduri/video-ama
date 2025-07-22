#!/usr/bin/env python3
"""Main entry point for video-ama application."""

import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from video_ama.api.app import app


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "video_ama.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()