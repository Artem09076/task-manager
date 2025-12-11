from src.api.router import router  
from starlette.responses import Response
from starlette.requests import Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@router.get("/metrics")
async def metrics(request: Request) -> Response:

    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)