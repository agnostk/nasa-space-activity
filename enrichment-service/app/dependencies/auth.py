from fastapi import Header, HTTPException, status, Request

from app.config import API_KEY


def verify_api_key(x_api_key: str = Header(...), request: Request = None):
    # Allow public access to health/docs
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
