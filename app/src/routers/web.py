from fastapi import APIRouter, Request
from ..templates.main import templates
from pydantic import BaseModel

router = APIRouter(tags=["web"])

@router.get("/")
def root(request: Request):
    """
    Root endpoint to serve the HTML frontend.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/health")
def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}