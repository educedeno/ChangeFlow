"""Punto de entrada de la API FastAPI."""

from fastapi import FastAPI

from app.api.routes import requests as requests_router

app = FastAPI(title="ChangeFlow API")

app.include_router(requests_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}