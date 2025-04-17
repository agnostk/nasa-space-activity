from fastapi import FastAPI, Depends
from app.routers import neo_threat_score, image_metadata
from app.dependencies.auth import verify_api_key

app = FastAPI(
    title='NASA NEO Threat API',
    version='1.0.0',
    dependencies=[Depends(verify_api_key)]
)

app.include_router(neo_threat_score.router)
app.include_router(image_metadata.router)
