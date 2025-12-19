from fastapi import APIRouter, HTTPException, Response
from app.logger import get_logger
from pydantic import BaseModel
from app.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()
logger = get_logger(__name__)

class QueryRequest(BaseModel):
    query: str
    propertyId: str | None = None

@router.post("/query")
def query_endpoint(req: QueryRequest):
    logger.info("Received query request: %s, propertyId=%s", req.query, req.propertyId)
    result = orchestrator.handle_query(
        question=req.query,
        property_id=req.propertyId
    )

    answer_text = result.get("answer", "No answer available.")
    logger.info("Query result: intent=%s, rows(seo)=%s, rows(analytics)=%s",
                result.get("intent"),
                (len(result.get("seo", {}).get("results", [])) if result.get("seo") else None),
                (result.get("analytics", {}).get("row_count") if result.get("analytics") else None)
                )

    return Response(content=answer_text, media_type="text/plain")