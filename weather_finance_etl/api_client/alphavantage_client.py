import requests
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = 'X1QPTDWI5ZSOF0Y9'
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    @staticmethod
    def fetch_daily(symbol, outputsize="compact"):
        response = requests.get(
            AlphaVantageClient.BASE_URL,
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": outputsize,
                "apikey": API_KEY
            }
        )
        return response.json()

    @staticmethod
    def fetch_intraday(symbol, interval="60min", outputsize="compact"):
        response = requests.get(
            AlphaVantageClient.BASE_URL,
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": API_KEY
            }
        )
        return response.json()
