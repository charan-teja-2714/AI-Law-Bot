from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.db.database import init_db

app = FastAPI(title="AI Law Bot API", version="2.0.0", description="Indian Legal RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

init_db()

app.include_router(routes.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "AI Law Bot API is running",
        "version": "2.0.0",
        "description": "Indian Legal RAG Assistant"
    }
