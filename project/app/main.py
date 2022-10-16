import logging

from fastapi import FastAPI

from app.api import agent

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(agent.router)

    return application


app = create_application()
