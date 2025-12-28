"""
FastAPI server entry point.
Run with: uvicorn server:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(
    title="GuppShupp Memory & Personality API",
    description="AI-powered memory extraction and personality transformation for companion AI",
    version="1.0.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "GuppShupp Memory & Personality API",
        "version": "1.0.0",
        "endpoints": {
            "extract": "POST /api/extract - Extract memory from messages",
            "respond": "POST /api/respond - Generate personality response",
            "compare": "POST /api/compare - Compare all personalities",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
