from fastapi import APIRouter, Request
from ..templates.main import templates
from pydantic import BaseModel
from ..rag.rag import SimpleRAGPipeline
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from bs4 import BeautifulSoup
from urllib.parse import unquote_plus

router = APIRouter(tags=["web"])

ragpipeline = SimpleRAGPipeline()

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

@router.get("/context")
def retrieve_context(request: Request, prompt: str):
    """
    Retrieve context based on the query using the RAG pipeline.
    """
    print(f"Received query: {prompt}")
    contexts = ragpipeline.retrieve_context(prompt, top_k=10)
    return templates.TemplateResponse("context.html", {
        "request": request,
        "context": contexts,
    }   )