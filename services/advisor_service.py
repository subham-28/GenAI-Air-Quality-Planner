from services.geocoding_service import get_coordinates
from services.air_quality_service import get_air_quality
from services.weather_service import get_weather
from services.data_service import extract_curr_data
from services.aqi_engine import get_overall_category, generate_basic_recommendation
from services.rag_service import ask_guidelines, get_guideline_retrieval_status
from services.time_window_service import find_best_and_worst_windows
from services.confidence_service import calculate_confidence


def get_air_quality_plan(city, profile, activity, duration_minutes, location=None):
    if location is None:
        location = get_coordinates(city)

    if location is None:
        return {
            "error": "City not found. Please try another city name."
        }

    pollution = get_air_quality(location["latitude"], location["longitude"])
    weather = get_weather(location["latitude"], location["longitude"])

    time_window_result = find_best_and_worst_windows(
    pollution=pollution,
    duration_minutes=duration_minutes
)

    data = extract_curr_data(location, pollution, weather)

    result = get_overall_category(data["pm2_5"], data["pm10"])

    suggestion = generate_basic_recommendation(
        result["overall_category"],
        profile,
        activity
    )

    plan = {
        "city": data["city"],
        "country": data["country"],
        "time": data["time"],

        "matched_location": location.get("display_name"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),

        "pm2_5": data["pm2_5"],
        "pm10": data["pm10"],
        "us_aqi": data["us_aqi"],
        "european_aqi": data["european_aqi"],

        "carbon_monoxide": data.get("carbon_monoxide"),
        "nitrogen_dioxide": data.get("nitrogen_dioxide"),
        "sulphur_dioxide": data.get("sulphur_dioxide"),
        "ozone": data.get("ozone"),

        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "wind_speed": data["wind_speed"],
        "precipitation": data["precipitation"],

        "pm25_category": result["pm25_category"],
        "pm10_category": result["pm10_category"],
        "overall_category": result["overall_category"],
        "dominant_pollutant": result["dominant_pollutant"],

        "profile": profile,
        "activity": activity,
        "duration_minutes": duration_minutes,
        "recommendation": suggestion,

        "best_outdoor_window": time_window_result.get("best_window"),
        "worst_outdoor_window": time_window_result.get("worst_window"),
        "best_window_avg_pm25": time_window_result.get("best_avg_pm25"),
        "best_window_avg_pm10": time_window_result.get("best_avg_pm10"),
        "worst_window_avg_pm25": time_window_result.get("worst_avg_pm25"),
        "worst_window_avg_pm10": time_window_result.get("worst_avg_pm10"),
        "hourly_forecast": time_window_result.get("hourly_forecast"),
    }

    rag_question = f"""
The user is asking for an air quality action recommendation.

Current air quality summary:
- Overall AQI category: {plan.get('overall_category')}
- Dominant pollutant: {plan.get('dominant_pollutant')}
- PM2.5: {plan.get('pm2_5')} µg/m³
- PM10: {plan.get('pm10')} µg/m³
- Carbon monoxide: {plan.get('carbon_monoxide')}
- Nitrogen dioxide: {plan.get('nitrogen_dioxide')}
- Sulphur dioxide: {plan.get('sulphur_dioxide')}
- Ozone: {plan.get('ozone')}
- US AQI: {plan.get('us_aqi')}
- European AQI: {plan.get('european_aqi')}

Current weather summary:
- Temperature: {plan.get('temperature')} °C
- Humidity: {plan.get('humidity')} %
- Wind speed: {plan.get('wind_speed')} km/h
- Precipitation: {plan.get('precipitation')} mm

Best/worst outdoor timing based on hourly PM forecast:
- Best outdoor window today: {plan.get('best_outdoor_window')}
- Average PM2.5 during best window: {plan.get('best_window_avg_pm25')} µg/m³
- Average PM10 during best window: {plan.get('best_window_avg_pm10')} µg/m³
- Worst outdoor window today: {plan.get('worst_outdoor_window')}
- Average PM2.5 during worst window: {plan.get('worst_window_avg_pm25')} µg/m³
- Average PM10 during worst window: {plan.get('worst_window_avg_pm10')} µg/m³

User details:
- Profile: {plan.get('profile')}
- Activity: {plan.get('activity')}
- Duration: {plan.get('duration_minutes')} minutes

Basic rule-based recommendation:
{plan.get('recommendation')}

Using the provided CPCB and WHO air quality guideline context, explain:
1. Whether the user should continue, reduce, postpone, or avoid the activity.
2. Why this recommendation is suitable.
3. Which pollutant is the main concern.
4. How weather conditions may affect the recommendation if relevant.
5. A safer alternative action.

Do not give medical diagnosis or medicine advice.
Give general public air-quality guidance only.
"""
    
    retrieval_status = get_guideline_retrieval_status(rag_question)

    rag_explanation = ask_guidelines(
    rag_question,
    apply_safety_guard=False
)

    plan["rag_explanation"] = rag_explanation

    confidence_result = calculate_confidence(
    plan=plan,
    retrieval_status=retrieval_status
)

    plan["confidence_label"] = confidence_result.get("confidence_label")
    plan["confidence_score"] = confidence_result.get("confidence_score")
    plan["confidence_reasons"] = confidence_result.get("confidence_reasons")
    plan["retrieved_guideline_chunks"] = confidence_result.get("retrieved_guideline_chunks")

    return plan