from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import neo_threat_score, image_metadata, mosaic_generator

app = FastAPI(
    title='NASA NEO Threat API',
    version='1.0.0',
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(neo_threat_score.router)
app.include_router(image_metadata.router)
app.include_router(mosaic_generator.router)
