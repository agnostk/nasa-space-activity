from fastapi import APIRouter, HTTPException, Depends

from app.dependencies.auth import verify_api_key
from app.models import NeoThreatScoreRequest, NeoThreatScoreResponse
from app.services.threat_score import get_threat_score

router = APIRouter()


@router.post('/neo-threat-score', response_model=NeoThreatScoreResponse, dependencies=[Depends(verify_api_key)])
def compute_threat_score(request: NeoThreatScoreRequest):
    try:
        threat_score = get_threat_score(
            request.diameter_min_km,
            request.diameter_max_km,
            request.velocity_kph,
            request.miss_distance_km,
            request.hazardous
        )
        return {'threat_score': threat_score}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Internal error: {str(e)}')
