import requests
from geopy.geocoders import Nominatim


from .settings import (
    SENSORS_AFRICA_API,
    SENSORS_AFRICA_API_KEY,
)


def address_converter(lat_long):
    geolocator = Nominatim(user_agent="sensors-api")
    location = geolocator.reverse(lat_long)
    location.raw["address"].update({"display_name": location.address})
    return location.raw["address"]

def get_sensors_africa_locations():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/locations/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    locations = []

    if response.ok:
        """
        Using latitude, longitude as a key and location id as value to help us
        find already existing location latter without having to ping the server
        Using round ensures latitude, longitude value will be the same as
        lat_log in the run method.
        """
        for location in response.json():
            loc = {
                f"{round(float(location['latitude']), 3)}, {round(float(location['longitude']), 3)}": f"{location['id']}"
            }
            locations.append(loc)

    return locations

def create_location(location):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/locations/",
        data=location,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]
    else:
        raise Exception(response.text)


def get_sensors_africa_nodes():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/nodes/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()
    return []


def create_node(node):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/nodes/",
        data=node,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]
