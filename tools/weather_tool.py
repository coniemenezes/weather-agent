import requests

from config.settings import API_WEATHER

from config.constants import (
    OPENWEATHER_URL,
    REQUEST_TIMEOUT,
    COUNTRIES,
    FAHRENHEIT_COUNTRIES
)


def get_weather(city: str):
    """
    Get weather for a given city.
    """

    if not API_WEATHER:
        return {
            "error": "API_WEATHER não configurada."
        }

    try:

        response = requests.get(
            OPENWEATHER_URL,
            params={
                "q": city,
                "appid": API_WEATHER,
                "units": "metric",
                "lang": "pt_br"
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        main = data.get("main", {})

        weather = data.get(
            "weather",
            [{}]
        )[0]

        wind = data.get(
            "wind",
            {}
        )

        sys_data = data.get(
            "sys",
            {}
        )

        temp_c = main.get("temp")

        temp_f = round(
            (temp_c * 9 / 5) + 32,
            2
        )

        country_code = sys_data.get(
            "country",
            ""
        )

        country_name = COUNTRIES.get(
            country_code,
            country_code
        )

        preferred_unit = (
            "fahrenheit"
            if country_name in FAHRENHEIT_COUNTRIES
            else "celsius"
        )

        return {
            "city": data.get("name"),
            "country": country_name,
            "condition": weather.get("description"),
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": temp_f,
            "preferred_unit": preferred_unit,
            "humidity": main.get("humidity"),
            "wind_speed": wind.get("speed")
        }

    except requests.exceptions.HTTPError:

        return {
            "error": f"Não encontrei clima para {city}"
        }

    except requests.exceptions.RequestException as exc:

        return {
            "error": str(exc)
        }