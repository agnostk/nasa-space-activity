def get_threat_score(
        diameter_min_km: float,
        diameter_max_km: float,
        velocity_kph: float,
        miss_distance_km: float,
        hazardous: bool) -> float:
    # Normalize each component
    avg_diameter = (diameter_min_km + diameter_max_km) / 2
    velocity_score = min(velocity_kph / 100000, 1.0)
    distance_score = min(1.0 / miss_distance_km, 1.0)
    size_score = min(avg_diameter / 1.0, 1.0)  # 1km as baseline threat
    hazard_bonus = 0.3 if hazardous else 0.0

    score = min(size_score * 0.3 + velocity_score * 0.2 + distance_score * 0.2 + hazard_bonus, 1.0)
    return score
