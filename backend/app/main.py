from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine

from app.api.router import api_router

# Create database tables (For dev only. In prod use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Network Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Network Dashboard API"}

app.include_router(api_router, prefix="/api/v1")
