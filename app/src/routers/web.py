from fastapi import APIRouter, Request
from ..templates.main import templates

router = APIRouter(tags=["web"])

@router.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
