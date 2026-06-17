def get_pm25_category(pm25):
    if pm25 is None:
        return "Unknown"
    if pm25 <= 30:
        return "Good"
    elif pm25 <= 60:
        return "Satisfactory"
    elif pm25 <= 90:
        return "Moderately Polluted"
    elif pm25 <= 120:
        return "Poor"
    elif pm25 <= 250:
        return "Very Poor"
    else:
        return "Severe"


def get_pm10_category(pm10):
    if pm10 is None:
        return "Unknown"
    if pm10 <= 50:
        return "Good"
    elif pm10 <= 100:
        return "Satisfactory"
    elif pm10 <= 250:
        return "Moderately Polluted"
    elif pm10 <= 350:
        return "Poor"
    elif pm10 <= 430:
        return "Very Poor"
    else:
        return "Severe"
    


RANK = {
    "Unknown": 0,
    "Good": 1,
    "Satisfactory": 2,
    "Moderately Polluted": 3,
    "Poor": 4,
    "Very Poor": 5,
    "Severe": 6
}


def get_overall_category(pm25, pm10):
    pm25_category=get_pm25_category(pm25)
    pm10_category=get_pm10_category(pm10)

    if RANK[pm25_category]>=RANK[pm10_category]:
        return {
            "overall_category": pm25_category,
            "dominant_pollutant": "PM2.5",
            "pm25_category": pm25_category,
            "pm10_category": pm10_category
        }
    else:
        return {
            "overall_category": pm10_category,
            "dominant_pollutant": "PM10",
            "pm25_category": pm25_category,
            "pm10_category": pm10_category
        }
    

def generate_basic_recommendation(category,profile,activity):
    category=category.lower()
    activity=activity.lower()
    profile=profile.lower()

    if category in ["good","satisfactory"]:
        return "Outdoor activity is generally okay. Prefer low-traffic areas if possible."

    elif category=="moderately polluted":
        if "jog" in activity or "run" in activity or "cycling" in activity:
            return "You can go outside, but avoid long or intense outdoor exercise."
        else:
            return "Short outdoor activity is acceptable, but avoid staying outside for too long."

    elif category=="poor":
        if "jog" in activity or "run" in activity or "cycling" in activity:
            return "Avoid outdoor high-intensity exercise right now. Prefer indoor activity."
        else:
            return "Limit outdoor exposure and avoid polluted roads or traffic-heavy areas."

    elif category=="very poor":
        return "Avoid unnecessary outdoor activity. Keep outdoor exposure short."

    elif category=="severe":
        return "Avoid outdoor activity unless necessary."

    else:
        return "Air quality data is unavailable, so a reliable recommendation cannot be generated."
    