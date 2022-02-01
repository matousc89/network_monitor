"""Interactive leaflet map

This script allows the user to visualize the data in an interactive map.

The user can customize some of the map parameters in the config.

This script requires that `folium` and `webbrowser` be installed within
the Python environment you are running this script in.

Folium makes it easy to visualize data that has been manipulated in
Python on an interactive leaflet map.

"""


import json
import os

import webbrowser
import folium

from storages.engines import get_reader_engine


def get_warning_color(value):
    """Setting up the ranges provided in the config."""
    for key, ranges in warning_colors.items():
        if ranges["min"] < value <= ranges["max"]:
            return key
    return default_color


"""Loading the config parameters."""
with open("config.json", "r") as f:
    config = json.loads(f.read())

server_info = config["server_info"]
map_settings = config["map_settings"]
warning_colors = map_settings["warning_colors"]
default_color = map_settings["default_color"]
user_lat = float(map_settings["user_latitude"])
user_lon = float(map_settings["user_longitude"])
user_city = map_settings["user_location"]
round_digits = int(map_settings["round_digits"])
OPEN_BROWSER = map_settings["open_browser"]

# getting the dataframe
storage_engine = get_reader_engine(config["writer_settings"]["engine"])
dfs = storage_engine.get_tables()
data = dfs["ping"]

# making the map, center according to users location
my_map = folium.Map(
    location=(user_lat, user_lon),
    zoom_start=2,
    max_bounds=True,
    min_zoom=2
)
# showing users location with a gray marker
folium.Marker(
    location=(user_lat, user_lon),
    popup=user_city,
    tooltip="User",
    icon=folium.Icon(prefix="fa", icon="circle", color="gray")
).add_to(my_map)

for address, values in server_info.items():
    city = values["location"]
    latitude = values["latitude"]
    longitude = values["longitude"]
    subset = data[data["address"] == address]

    if subset.empty:
        continue

    last_ping = round(subset["value"].iloc[-1], round_digits)
    average_ping = round(subset["value"].median(), round_digits)

    tooltip = """
    <table>
      <tr>
        <td>Address:</td>
        <td><b>{}</b></td>
      </tr>
      <tr>
        <td>Last ping:</td>
        <td><b>{}</b></td>
      </tr>
      <tr>
        <td>Median ping:</td>
        <td><b>{}</b></td>
      </tr>
    </table>
    """.format(address, last_ping, average_ping)

    folium.Marker(
        location=(latitude, longitude),
        popup=city,
        tooltip=tooltip,
        icon=folium.Icon(prefix="fa", icon="circle")
    ).add_to(my_map)

    folium.PolyLine(locations=[(user_lat, user_lon), (latitude, longitude)],
                    color=get_warning_color(average_ping),
                    weight=2,
                    opacity=0.7).add_to(my_map)

def open_local_file():
    """Opening the html file in a browser."""
    webbrowser.open('file://' + os.path.realpath("my_map.html"))

my_map.save("my_map.html")

if OPEN_BROWSER:
    open_local_file()

