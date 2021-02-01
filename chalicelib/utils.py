import requests
from geopy.geocoders import Nominatim
import awoc
from pycountry_convert import country_name_to_country_alpha2


from .settings import (
    SENSORS_AFRICA_API,
    SENSORS_AFRICA_API_KEY,
)

def get_country_code(country):
  try:
    return country_name_to_country_alpha2(country)
  except:
    return

def get_african_countries_codes():
  countries = awoc.AWOC().get_countries_list_of('Africa')
  return [get_country_code(country).upper() for country in countries if get_country_code(country)]

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

def get_sensors_africa_sensor_types():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/sensor-types/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return [
            {f"{sensor_type['uid']}": sensor_type["id"]}
            for sensor_type in response.json()
        ]
    return []

def create_sensor_type(sensor_type):
    data = {
            "uid": sensor_type["name"],
            "name": sensor_type["name"],
            "manufacturer": sensor_type["manufacturer"],
        }
    response = requests.post(
            f"{SENSORS_AFRICA_API}/v2/sensor-types/",
            data=data,
            headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
        )
    if response.ok:
        return response.json()["id"]
    else:
        raise Exception(response.text)

def get_sensor_id(sensor_details):
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/sensors/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    for sensor in response.json():
        if sensor['node'] == sensor_details['node'] and sensor['sensor_type'] == sensor_details['sensor_type'] and sensor['pin'] == sensor_details['pin']:
            return sensor['id']

def create_sensor(sensor):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/sensors/",
        data=sensor,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]
    else:
        raise Exception(response.text)

def send_sensor_data(sensor_id, sensor_data_values, timestamp=None):
    sensordatavalues = []
    for sensor_data_value in sensor_data_values['sensordatavalues']:
        if sensor_data_value['value_type'] in ['humidity', 'temperature', 'pressure', 'P1', 'P2', 'P10']:
            sensordatavalues.append(
                {"value": sensor_data_value['value'], "value_type": sensor_data_value['value_type']},
            )
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v1/push-sensor-data/",
        json={"sensordatavalues": sensordatavalues},
        headers={
            "SENSOR": str(sensor_id),
            "Authorization": f"Token {SENSORS_AFRICA_API_KEY}",
        },
    )

    return response.json()
