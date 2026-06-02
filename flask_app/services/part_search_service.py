import os
import requests
from dotenv import load_dotenv

#load environment variables from .env
load_dotenv()

# Backend search API endpoint
SEARCH_API_URL = os.getenv("SEARCH_API_URL")


def search_part_data(apn, input_site_code):
    # Validate required configuration before making the request
    if not SEARCH_API_URL:
        return {
            "error": "SEARCH_API_URL is missing. Add it to your .env file."
        }, 500

    # Build request payload for the search API
    payload = {
        "apn": apn,
        "input_site_code": input_site_code
    }

    # submit search request and return API response
    response = requests.post(
        SEARCH_API_URL,
        json=payload,
        timeout=60
    )

    return response.json(), response.status_code