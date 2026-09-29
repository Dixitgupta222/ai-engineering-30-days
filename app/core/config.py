import logging
import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
if APP_ENV not in ("development", "production"):
    raise ValueError(
        f"Invalid APP_ENV: {APP_ENV}. "
        "Use 'development' or 'production'."
    )

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


def configure_logging():
    log_level = logging.INFO

    if APP_ENV == "production":
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.getLogger().setLevel(log_level)