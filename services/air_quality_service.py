# # Fetch air quality from the lat and lon

# import requests

# def get_air_quality(lat,lon):
#   url="https://air-quality-api.open-meteo.com/v1/air-quality"

#   params= {
#         "latitude": lat,
#         "longitude": lon,
#         "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi",
#         "hourly": "pm10,pm2_5,us_aqi,european_aqi",
#         "timezone": "auto"
#     }

#   response=requests.get(url,params=params)
#   data=response.json()
#   return data["current"]


# Fetch air quality from latitude and longitude

import requests


def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,

        # Current values for dashboard/action plan
        "current": (
            "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,"
            "sulphur_dioxide,ozone,us_aqi,european_aqi"
        ),

        # Hourly forecast values for best/worst outdoor window
        "hourly": "pm10,pm2_5,us_aqi,european_aqi",

        # Only today's forecast
        "forecast_days": 1,

        # Gives local city time
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data