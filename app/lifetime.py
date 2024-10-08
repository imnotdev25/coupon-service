from fastapi import FastAPI

from app.database import init_db, close_db


def startup(app: FastAPI):
    def _startup():
        init_db()

    return _startup


def shutdown(app: FastAPI):
    def _shutdown():
        close_db()

    return _shutdown
