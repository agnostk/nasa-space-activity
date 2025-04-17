from fastapi import APIRouter, Depends, HTTPException
from app.models import ImageMetadataRequest, ImageMetadataResponse
from app.services.analyze_image import analyze_image
from app.dependencies.auth import verify_api_key

router = APIRouter()


@router.post('/image-meta', response_model=ImageMetadataResponse)
def extract_image_metadata(
        payload: ImageMetadataRequest,
        auth: None = Depends(verify_api_key)
):
    try:
        metadata = analyze_image(str(payload.image_url))
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Image analysis failed: {str(e)}')
