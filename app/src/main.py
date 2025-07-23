from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers.web import router as web_router


app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(web_router)