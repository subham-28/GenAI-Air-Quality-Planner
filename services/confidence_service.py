def calculate_confidence(plan, retrieval_status=None):
    """
    Calculates confidence based on:
    - location clarity
    - PM2.5 / PM10 availability
    - AQI category availability
    - pollutant completeness
    - guideline retrieval strength
    """

    score = 0
    reasons = []


    if plan.get("matched_location") and plan.get("latitude") and plan.get("longitude"):
        score += 20
        reasons.append("Location was clearly resolved.")
    else:
        reasons.append("Location match is unclear.")


    pm25_available = plan.get("pm2_5") is not None
    pm10_available = plan.get("pm10") is not None

    if pm25_available and pm10_available:
        score += 30
        reasons.append("Both PM2.5 and PM10 values are available.")
    elif pm25_available or pm10_available:
        score += 15
        reasons.append("Only one of PM2.5 or PM10 is available.")
    else:
        reasons.append("PM2.5 and PM10 values are missing.")


    category = plan.get("overall_category")

    if category and category != "Unknown":
        score += 20
        reasons.append("AQI category was successfully calculated.")
    else:
        reasons.append("AQI category could not be calculated reliably.")


    pollutant_keys = [
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
        "us_aqi",
        "european_aqi"
    ]

    available_pollutants = [
        key for key in pollutant_keys
        if plan.get(key) is not None
    ]

    if len(available_pollutants) >= 4:
        score += 15
        reasons.append("Most supporting pollutant values are available.")
    elif len(available_pollutants) >= 2:
        score += 8
        reasons.append("Only partial supporting pollutant values are available.")
    else:
        reasons.append("Supporting pollutant data is limited.")


    retrieval_status = retrieval_status or {}

    retrieved_chunks = retrieval_status.get("retrieved_chunks", 0)

    if retrieved_chunks >= 3:
        score += 15
        reasons.append("Relevant CPCB/WHO guideline chunks were retrieved.")
    elif retrieved_chunks >= 1:
        score += 8
        reasons.append("Only limited guideline context was retrieved.")
    else:
        reasons.append("Guideline retrieval context was weak or unavailable.")


    if score >= 80:
        label = "High"
    elif score >= 50:
        label = "Medium"
    else:
        label = "Low"

    return {
        "confidence_label": label,
        "confidence_score": score,
        "confidence_reasons": reasons,
        "retrieved_guideline_chunks": retrieved_chunks
    }