from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.orchestrator import handle_query

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    propertyId: str | None = None

@router.post("/query")
def query_endpoint(req: QueryRequest):
    return handle_query(req)
