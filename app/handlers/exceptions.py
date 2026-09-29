import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
):
    logger.error(
        "Database error occurred: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unexpected error occurred: %s",
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )