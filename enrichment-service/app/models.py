from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class NeoThreatScoreRequest(BaseModel):
    diameter_min_km: float
    diameter_max_km: float
    velocity_kph: float
    miss_distance_km: float
    hazardous: bool


class NeoThreatScoreResponse(BaseModel):
    threat_score: float = Field(..., ge=0.0, le=1.0)


class ImageMetadataRequest(BaseModel):
    image_url: HttpUrl


class RGBColor(BaseModel):
    r: int
    g: int
    b: int


class ImageMetadataResponse(BaseModel):
    average_color: RGBColor
    image_hash: str
    width: int
    height: int
    content_type: Optional[str]
