"""
FastAPI routes for memory extraction and personality generation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.models.memory import UserMemory
from src.models.messages import ChatMessage
from src.models.personality import PersonalityResponse
from src.extractors.orchestrator import MemoryOrchestrator
from src.personality.engine import PersonalityEngine
from src.llm.client import GroqClient

router = APIRouter()

# Initialize clients (singleton pattern)
_groq_client = None
_memory_orchestrator = None
_personality_engine = None


def get_groq_client() -> GroqClient:
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client


def get_memory_orchestrator() -> MemoryOrchestrator:
    global _memory_orchestrator
    if _memory_orchestrator is None:
        _memory_orchestrator = MemoryOrchestrator(get_groq_client())
    return _memory_orchestrator


def get_personality_engine() -> PersonalityEngine:
    global _personality_engine
    if _personality_engine is None:
        _personality_engine = PersonalityEngine(get_groq_client())
    return _personality_engine


# Request/Response Models
class ExtractRequest(BaseModel):
    messages: list[ChatMessage]


class RespondRequest(BaseModel):
    query: str
    memory: UserMemory
    personality_id: str


class CompareRequest(BaseModel):
    query: str
    memory: UserMemory


# Routes
@router.post("/extract", response_model=UserMemory)
async def extract_memory(request: ExtractRequest):
    """
    Extract user memory from conversation history.
    
    Uses parallel extraction with asyncio.gather for:
    - Preferences
    - Emotional patterns
    - Facts
    """
    try:
        orchestrator = get_memory_orchestrator()
        return await orchestrator.extract_all(request.messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond", response_model=PersonalityResponse)
async def generate_response(request: RespondRequest):
    """
    Generate a personality-adjusted response.
    
    Takes user query, memory context, and personality ID.
    Returns a response tailored to that personality.
    """
    try:
        engine = get_personality_engine()
        return await engine.generate_response(
            query=request.query,
            memory=request.memory,
            profile_id=request.personality_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_personalities(request: CompareRequest):
    """
    Generate responses from all personalities for comparison.
    
    Returns a dict mapping personality_id to PersonalityResponse.
    """
    try:
        engine = get_personality_engine()
        return await engine.generate_comparison(
            query=request.query,
            memory=request.memory,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
