import requests
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
class AmadeusAPI:
    def __init__(self):

        self.client_id = os.getenv("API_KEY_AMADEUS")
        self.client_secret = os.getenv("API_SECRET")
        self.token = self.get_token()
        self.url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

        self.headers = {
            "Authorization": f"Bearer {self.token}",
        }
    def get_token(self):
        url_token = "https://test.api.amadeus.com/v1/security/oauth2/token"

        headers = {
            "Content-type": "application/x-www-form-urlencoded"
        }

        data_api = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(url=url_token, headers=headers, data=data_api)
        response.raise_for_status()
        return response.json()["access_token"]

    def make_request(self, origin, destination, departure_date, maxprice=None ):
        params = {
            "originLocationCode": f"{origin}",
            "destinationLocationCode": f"{destination}",
            # "maxPrice": maxprice,
            "departureDate": f"{departure_date}",
            "adults": 1,
            "nonStop": "true",
            "max": 10,
            "travelClass": "ECONOMY"
        }
        if maxprice is not None:
            params["maxPrice"] = maxprice

        response = requests.get(url=self.url,headers= self.headers, params=params)
        return response.json()


    def city_to_iata(self, city):
        params = {
            "keyword": f"{city}".upper()
        }
        response = requests.get(url="https://test.api.amadeus.com/v1/reference-data/locations/cities",headers=self.headers, params=params)
        data = response.json()
        if data.get("data") and len(data["data"]) >0:
            return data["data"][0]["iataCode"]
        else:
            return None