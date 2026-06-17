# # Fetch Lat Lon from a place name
# import requests

# def get_coordinates(city,country_code="IN"):
#   url="https://geocoding-api.open-meteo.com/v1/search"
#   params= {
#       "name": city,
#       "count": 10,
#       "language": "en",
#       "format": "json",
#       "countryCode": country_code
#   }
#   response=requests.get(url,params=params)
#   data=response.json()

#   if 'results' not in data:
#     return None

#   data=data['results'][0]

#   return {
#       "city": data['name'],
#       "country": data['country'],
#       "latitude": data['latitude'],
#       "longitude": data['longitude']
#   }



# # Fetch Lat Lon from a place name


import requests

def search_locations(city, country_code="IN", count=10):

    if not city or not city.strip():
        return []

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city.strip(),
        "count": count,
        "language": "en",
        "format": "json",
        "countryCode": country_code
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            return []

        locations = []

        for item in data["results"]:
            city_name = item.get("name")
            admin1 = item.get("admin1")
            admin2 = item.get("admin2")
            country = item.get("country")
            latitude = item.get("latitude")
            longitude = item.get("longitude")

            display_parts = [
                part for part in [city_name, admin2, admin1, country]
                if part
            ]

            display_name = ", ".join(display_parts)

            locations.append({
                "city": city_name,
                "admin1": admin1,
                "admin2": admin2,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "display_name": display_name
            })

        return locations

    except requests.exceptions.RequestException:
        return []


def get_coordinates(city, country_code="IN"):
    locations = search_locations(
        city=city,
        country_code=country_code,
        count=1
    )

    if not locations:
        return None

    return locations[0]