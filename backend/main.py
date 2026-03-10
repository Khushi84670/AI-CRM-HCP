from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import Base, engine
from routers import interactions, ai


# Create DB tables on startup (for demo / assignment use)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM HCP Interaction API",
    version="1.0.0",
    description="Backend API for AI-powered HCP interaction logging.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interactions.router, prefix="/api", tags=["interactions"])
app.include_router(ai.router, prefix="/api", tags=["ai"])


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

