from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Cover Letter Generator")
app.include_router(router, prefix="/api/v1")
