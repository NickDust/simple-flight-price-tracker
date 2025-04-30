from dotenv import load_dotenv, find_dotenv
import os
import requests
class GoogleSheet:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.token = os.getenv("TOKEN_G_SHEET")
        self.url = "https://api.sheety.co/c501fd85fc5a422ceb32fc28d743bae8/flightTickets/foglio1"

        self.header = {
            "Authorization": f"Bearer {self.token}"
        }

    def make_request(self):
        response = requests.get(url=self.url, headers=self.header)
        data = response.json()

        result = []
        for row in data["foglio1"]:
            flight_data = {
                "id" : row["id"],
                "origin" : row.get("origin", ""),
                "destination" : row.get("destination",""),
                "price": row.get("price", ""),
                "iataCode": row.get("iataCode",""),
                "iataCodeD": row.get("iataCodeD",""),
                "date": row.get("date", "")
            }
            result.append(flight_data)
        return result

