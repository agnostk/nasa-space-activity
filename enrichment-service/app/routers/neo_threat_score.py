from fastapi import APIRouter, HTTPException

from app.models import NeoThreatScoreRequest, NeoThreatScoreResponse

router = APIRouter()


@router.post('/neo-threat-score', response_model=NeoThreatScoreResponse)
def compute_threat_score(request: NeoThreatScoreRequest):
    try:
        # Normalize each component
        avg_diameter = (request.diameter_min_km + request.diameter_max_km) / 2
        velocity_score = min(request.velocity_kph / 100000, 1.0)
        distance_score = min(1.0 / request.miss_distance_km, 1.0)
        size_score = min(avg_diameter / 1.0, 1.0)  # 1km as baseline threat
        hazard_bonus = 0.3 if request.hazardous else 0.0

        score = min(size_score * 0.3 + velocity_score * 0.2 + distance_score * 0.2 + hazard_bonus, 1.0)

        return {'threat_score': round(score, 4)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Internal error: {str(e)}')
