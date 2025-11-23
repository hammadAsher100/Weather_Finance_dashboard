import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

# Hardcoded API key
API_KEY = "24da2304743fc80db79e5dc167bc66a9"

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class OpenWeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    @staticmethod
    def fetch_current_weather(city: str):
        cache_file = CACHE_DIR / f"weather_{city.lower()}.json"

        # Check cache (valid for 10 minutes)
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(minutes=10):
                with open(cache_file) as f:
                    return json.load(f)

        # Make API request
        try:
            response = requests.get(
                OpenWeatherClient.BASE_URL,
                params={"q": city, "appid": API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            # Save cache
            with open(cache_file, "w") as f:
                json.dump(data, f)
            return data
        except requests.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
