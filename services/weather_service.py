# Fetch the weather data from the lat lon

import requests

def get_weather(lat,lon):
  url="https://api.open-meteo.com/v1/forecast"

  params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "auto"
    }
  response=requests.get(url,params=params)
  data=response.json()
  return data["current"]