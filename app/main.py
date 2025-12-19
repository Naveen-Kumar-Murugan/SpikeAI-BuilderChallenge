from fastapi import FastAPI, Request
from app.api import router
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI()
app.include_router(router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
	logger.info("Incoming request %s %s", request.method, request.url.path)
	response = await call_next(request)
	logger.info("Completed %s %s -> %s", request.method, request.url.path, response.status_code)
	return response

