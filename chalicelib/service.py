import requests

from chalicelib import utils
from .settings import OWNER_ID

def get_sensor_type(node, sensor_types):
    node_sensor_type = node['sensor']['sensor_type']['name']
    for sensor_type in sensor_types:
        if node_sensor_type in sensor_type.keys():
            return sensor_type[node_sensor_type]

african_countries = utils.get_african_countries_codes()
sensors_africa_nodes = utils.get_sensors_africa_nodes()
sensor_types = utils.get_sensors_africa_sensor_types()

def run():
  for country in african_countries:
      URL = f"https://data.sensor.community/airrohr/v1/filter/country={country}"
      response = requests.get(URL)
      nodes = response.json()
      if nodes:
          for node in nodes:
              locations = utils.get_sensors_africa_locations()
              if node['id'] not in [_node["node"]["uid"] for _node in sensors_africa_nodes if _node["node"]]:
                  lat_log = f"{round(float(node['location']['latitude']), 3)}, {round(float(node['location']['longitude']), 3)}"
                  location = [loc.get(lat_log) for loc in locations if loc.get(lat_log)]
                  if location:
                      location = location[0]
                  else:
                      # Create location 
                      address = utils.address_converter(lat_log)

                      location = utils.create_location(
                          {
                              "location": address["display_name"],
                              "longitude": node.get("location").get('longitude'),
                              "latitude": node.get("location").get('latitude'),
                              "altitude": node.get("location").get('altitude'),
                              "owner": OWNER_ID,
                              "country": address.get("country"),
                              "city": address.get("city"),
                              "postalcode": address.get("postcode"),
                          }
                      )
                  
                  # Create a Node
                  node_id = utils.create_node(
                      node={
                          "uid": node['id'],
                          "owner": OWNER_ID,
                          "location": location,
                      }
                  )
              else:
                  # Node already exist
                  node_id = [
                    _node["node"]["id"]
                      for _node in nodes
                      if _node["node"]["uid"] == str(node["id"])
                  ]
                  if node_id:
                      node_id = node_id[0]

              if not node_id:
                  # This should not happen
                  raise Exception("Missing Node ID")
              else:
                  sensor_type = get_sensor_type(node, sensor_types)
                  if not sensor_type:
                      # Create sensor-type
                      sensor_type = utils.create_sensor_type(node['sensor']['sensor_type'])
                  
                  sensor_id = utils.get_sensor_id({"node": node_id, "sensor_type": sensor_type, "pin": node['sensor']['pin']})

                  if not sensor_id:
                    # Create sensor
                    sensor_id = utils.create_sensor({"node": node_id, "sensor_type": sensor_type, "pin": node['sensor']['pin']})

                  # Send sensor Data
                  utils.send_sensor_data(node['id'], node)
