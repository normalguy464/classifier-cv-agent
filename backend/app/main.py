from fastapi import FastAPI

from backend.app.core.settings import RuntimeSettings
from backend.app.infrastructure.bootstrap import build_application

app: FastAPI = build_application(RuntimeSettings())
