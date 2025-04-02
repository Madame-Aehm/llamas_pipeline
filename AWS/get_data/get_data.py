import os
import requests

def get_data(event, context):
    api_key = os.getenv("WEATHER_APIKEY")
    endpoint = f"http://api.openweathermap.org/data/2.5/weather?units=metric&appid={api_key}&q=london"
    response = requests.get(endpoint)
    if response.status_code == 200:
        response_json = response.json()
        weather_date = response_json["dt"]
        weather_city = response_json["name"]
        weather_temp = response_json["main"]["temp"]
        weather_feels = response_json["main"]["feels_like"]
        weather_description = response_json["weather"][0]["description"]
        return [weather_date, weather_city, weather_temp, weather_feels, weather_description]
            