from fastapi import APIRouter, HTTPException, Depends

from app.dependencies.auth import verify_api_key
from app.models import ImageMetadataRequest, ImageMetadataResponse
from app.services.analyze_image import analyze_image

router = APIRouter()


@router.post('/image-metadata', response_model=ImageMetadataResponse, dependencies=[Depends(verify_api_key)])
def extract_image_metadata(payload: ImageMetadataRequest):
    try:
        metadata = analyze_image(
            image_source=str(payload.image_url),
            is_s3=payload.is_s3
        )
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Image analysis failed: {str(e)}')
