from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
     return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )