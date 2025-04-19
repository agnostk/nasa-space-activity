from fastapi import HTTPException, status, Request, Security
from fastapi.security import APIKeyHeader

from app.config import API_KEY

header_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_api_key(x_api_key: str = Security(header_scheme), request: Request = None, ):
    # Allow public access to docs
    if request.url.path in ["/docs", "/openapi.json"]:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
