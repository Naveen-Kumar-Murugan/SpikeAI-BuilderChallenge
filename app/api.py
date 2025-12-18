from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

class QueryRequest(BaseModel):
    query: str
    propertyId: str | None = None

@router.post("/query")
def query_endpoint(req: QueryRequest):
    result = orchestrator.handle_query(
        question=req.query,
        property_id=req.propertyId
    )

    return {
        "answer": result.get("answer", "No answer could be generated.")
    }
