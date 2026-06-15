# tools/location_tool.py

import requests

from config.constants import (
    IPINFO_URL,
    REQUEST_TIMEOUT,
    COUNTRIES
)


def get_location() -> str:
    """
    Get user's current location using IP geolocation.

    Returns:
        City, Country when detected.
        LOCATION_NOT_FOUND when location cannot be detected.
    """

    try:
        response = requests.get(
            IPINFO_URL,
            headers={
                "User-Agent": "weather-assistant"
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        city = data.get("city")
        country_code = data.get("country", "")

        if not city or not country_code:
            return "LOCATION_NOT_FOUND"

        country_name = COUNTRIES.get(
            country_code,
            country_code
        )

        return f"{city}, {country_name}"

    except requests.exceptions.RequestException:
        return "LOCATION_NOT_FOUND"

    except ValueError:
        return "LOCATION_NOT_FOUND"