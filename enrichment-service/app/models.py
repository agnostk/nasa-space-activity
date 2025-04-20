from typing import Optional, Union, Literal

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
    image_url: Union[HttpUrl, str]
    is_s3: bool = False


class RGBColor(BaseModel):
    r: int
    g: int
    b: int


class Classification(BaseModel):
    top_class: str
    confidence: float


class ImageMetadataResponse(BaseModel):
    average_color: RGBColor
    image_hash: str
    width: int
    height: int
    classification: Optional[Classification] = None


class MosaicTile(BaseModel):
    source: Literal['apod', 'mars']
    id: str
    date: str
    s3_path: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    average_color: RGBColor
    classification: str


class MosaicGeneratorResponse(BaseModel):
    mosaic_tiles: list[MosaicTile]
