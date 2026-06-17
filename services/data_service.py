# def extract_curr_data(location,pollution,weather):
#   return {
#         "city": location["city"],
#         "country": location["country"],
#         "latitude": location["latitude"],
#         "longitude": location["longitude"],
#         "time": pollution["time"],
#         "pm2_5": pollution["pm2_5"],
#         "pm10": pollution["pm10"],
#         "us_aqi": pollution["us_aqi"],
#         "european_aqi": pollution["european_aqi"],
#         "carbon_monoxide": pollution["carbon_monoxide"],
#         "nitrogen_dioxide": pollution["nitrogen_dioxide"],
#         "sulphur_dioxide": pollution["sulphur_dioxide"],
#         "ozone": pollution["ozone"],
#         "temperature": weather["temperature_2m"],
#         "humidity": weather["relative_humidity_2m"],
#         "wind_speed": weather["wind_speed_10m"],
#         "precipitation": weather["precipitation"]
#     }


def extract_curr_data(location, pollution, weather):
    aq = pollution.get("current", pollution)
    current_weather = weather.get("current", weather)

    return {
        "city": location.get("city"),
        "admin1": location.get("admin1"),
        "admin2": location.get("admin2"),
        "country": location.get("country"),
        "display_name": location.get("display_name"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),

        "time": aq.get("time"),

        "pm2_5": aq.get("pm2_5"),
        "pm10": aq.get("pm10"),
        "us_aqi": aq.get("us_aqi"),
        "european_aqi": aq.get("european_aqi"),

        "carbon_monoxide": aq.get("carbon_monoxide"),
        "nitrogen_dioxide": aq.get("nitrogen_dioxide"),
        "sulphur_dioxide": aq.get("sulphur_dioxide"),
        "ozone": aq.get("ozone"),

        "temperature": current_weather.get("temperature_2m"),
        "humidity": current_weather.get("relative_humidity_2m"),
        "wind_speed": current_weather.get("wind_speed_10m"),
        "precipitation": current_weather.get("precipitation")
    }