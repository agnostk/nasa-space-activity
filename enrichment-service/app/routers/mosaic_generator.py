from fastapi import APIRouter, HTTPException, UploadFile, Form, File

from app.models import MosaicGeneratorResponse
from app.services.generate_mosaic import generate_mosaic

router = APIRouter()


@router.post('/mosaic_generator', response_model=MosaicGeneratorResponse)
def mosaic_generator(
        image: UploadFile = File(...),
        mosaic_size: int = Form(..., ge=1, le=128),
):
    try:
        mosaic = generate_mosaic(image, mosaic_size)
        return mosaic
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Mosaic generation failed: {str(e)}')
