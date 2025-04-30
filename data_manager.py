import requests


from flight_search import AmadeusAPI

from google_sheet import GoogleSheet

class DataHandler:
    def __init__(self):
        self.api = AmadeusAPI()
        self.google = GoogleSheet()

    def google_data(self):
        data = self.google.make_request()
        if not data:
            return []
        return data

    def cheap_flight_data(self):
        data = self.api
        result = []
        google_data = self.google_data()
        for row in google_data:
            origin = row["origin"]
            destination = row["destination"]
            iata_origin = data.city_to_iata(origin)
            iata_destination = data.city_to_iata(destination)
            response = data.make_request(origin=iata_origin,
                                             destination=iata_destination,
                                             departure_date="2025-09-01")
            if response and "data" in response and response["data"]:
                print(f"{origin}->{destination}")
                cheapest = min(response["data"],key=lambda f: float(f["price"]["total"]))
                price = float(cheapest["price"]["total"])
                departure_date = cheapest["itineraries"][0]["segments"][0]["departure"]["at"].split("T")[0]

                result.append({
                    "id": row["id"],
                    "origin": origin,
                    "destination": destination,
                    "iataCode": iata_origin,
                    "iataCodeD": iata_destination,
                    "price": price,
                    "date": departure_date

                })
            else: print(f"no flight for {origin}->{destination}")
            print(result)
        return result

    def check_and_update_sheets(self):
        alert = []
        data = self.google_data()
        flight = self.cheap_flight_data()
        for data_row in data:
            matching_flight = next((f for f in flight if f["id"] == data_row["id"]), None)
            if matching_flight:
                try:
                    current_price = float(data_row["price"])
                    if matching_flight["price"] < current_price:
                        json = {
                            "foglio1":
                                {
                                    "iataCode": matching_flight["iataCode"],
                                    "iataCodeD": matching_flight["iataCodeD"],
                                    "price": matching_flight["price"],
                                    "date": matching_flight["date"]

                                }
                        }
                        # print(json)

                        requests.put(url=f"https://api.sheety.co/c501fd85fc5a422ceb32fc28d743bae8/flightTickets/foglio1/{data_row["id"]}",
                                     headers=self.google.header,json=json)
                        alert = f"Flight offer found: {matching_flight["iataCode"]}--to-->{matching_flight["iataCodeD"]} for only {matching_flight["price"]} on {matching_flight["date"]}"
                        return alert
                except (ValueError, TypeError):
                    json = {
                        "foglio1":
                            {
                                "iataCode": matching_flight["iataCode"],
                                # "id": flight_row["id"],
                                "price": matching_flight["price"],
                                "date": matching_flight["date"]

                            }
                    }


                    requests.put(url=f"https://api.sheety.co/c501fd85fc5a422ceb32fc28d743bae8/flightTickets/foglio1/{data_row["id"]}",
                                 headers=self.google.header, json=json)

                    alert.append(f"Flight offer found: {matching_flight["iataCode"]}--to-->{matching_flight["iataCodeD"]} for only {matching_flight["price"]} on {matching_flight["date"]}")
                    return alert










