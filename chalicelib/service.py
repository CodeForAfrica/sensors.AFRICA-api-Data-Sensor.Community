import requests
import awoc
from pycountry_convert import country_name_to_country_alpha2

from chalicelib import utils
from .settings import OWNER_ID


def get_country_code(country):
  try:
    return country_name_to_country_alpha2(country)
  except:
    return

def get_african_countries_codes():
  countries = awoc.AWOC().get_countries_list_of('Africa')
  return [get_country_code(country).upper() for country in countries if get_country_code(country)]

african_countries = get_african_countries_codes()
sensors_africa_nodes = utils.get_sensors_africa_nodes()
locations = utils.get_sensors_africa_locations()

def run():
  for country in african_countries:
      URL = f"https://data.sensor.community/airrohr/v1/filter/country={country}"
      response = requests.get(URL)
      nodes = response.json()
      if nodes:
          for node in nodes:
              import pdb; pdb.set_trace()
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
              
              print(1)
