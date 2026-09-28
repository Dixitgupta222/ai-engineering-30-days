import logging

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import APP_ENV, configure_logging
from app.handlers.exceptions import (
    general_exception_handler,
    sqlalchemy_exception_handler,
)
from app.routes.follow_ups import router as follow_up_router
from app.routes.leads import router as leads_router

configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(title="AI Lead Analyzer API")

app.add_exception_handler(
    SQLAlchemyError,
    sqlalchemy_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)
app.include_router(leads_router)
app.include_router(follow_up_router)
@app.get("/")
def home():
    logger.info("Root endpoint accessed")
    return {"message": "AI Lead Analyzer API"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": APP_ENV,
        "service": "AI Lead Analyzer API"
    }
