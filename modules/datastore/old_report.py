"""Data Analysis

Imports in this file are not in requirements.
TODO: it should be heavily refactored or replaced (maybe another app)

"""
import json
import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
import folium

def responses2df(responses):
    return pd.DataFrame(responses, columns=['ip_address', 'time', 'value'])

def get_histogram(df):
    """Following function plots a Histogram representing the distribution
    of pings for all the addresses and a Histogram for each address.
    The Histogram can be customized with the parameters in the config."""
    path = "media"

    filename = "Histogram_of_"
    df.sort_values(
        by=["ip_address", "value"]
    )

    for address in df["ip_address"].unique():
        df1 = df[df["value"] > 0]
        subset = df1[df1["ip_address"] == address]
        subset = subset[subset["value"] < subset["value"].quantile(hist_outlier)]

        if len(subset) > hist_const:
            bins = min(100, len(subset) // 10)
            subset['value'].hist(bins=bins,
                                  histtype='step'
                                  )

    plt.legend(df1["ip_address"])
    plt.xlabel("Ping Values [s]")
    plt.ylabel("Number of occurrences")
    plt.title("Distribution of Ping Values")
    plt.savefig(str('{}/svg/{}{}.svg'.format(path, filename, "addresses")), format='svg', dpi=1200)
    plt.savefig(str('{}/png/{}{}.png'.format(path, filename, "addresses")), dpi=100)
    plt.clf()

    html_content = ["<h2>Histograms<br>(Distribution of pings)</h2>"]
    html_content.append("""
    <a download="{1}{2}.png" href={0}/png/{1}{2}.png" title="{2}">
    <img src="{0}/svg/{1}{2}.svg" title="Click to download" alt="image not found"/><br>
    """.format(path, filename, "addresses"))


    for address in df["ip_address"].unique():

        subset_all = df[df["ip_address"] == address]
        count_all = subset_all['value'].shape[0]  # not working
        count_online = subset_all[subset_all["value"] > 0].shape[0]  # not working
        subset = subset_all[0 < subset_all["value"]]
        subset = subset[subset["value"] < subset["value"].quantile(hist_outlier)]

        if len(subset) > hist_const:
            bins = min(100, len(subset) // 10)
            i = address
            subset["value"].hist(bins=bins,
                                 grid=False
                                 )
            plt.xlabel("Ping Values [s]")
            plt.ylabel("Number of occurrences")
            plt.title("Distribution of Ping Values for address: {}".format(address))
            txt = "Median value: {0} <br> Minimum value: {1} <br> Maximum value: {2} <br> Offline count: {3}".format(str(round(subset_all["value"].median(), round_digits)), str(round(subset["value"].min(), round_digits)), str(round(subset_all["value"].max(), round_digits)), count_all - count_online)
            plt.savefig(str('{}/svg/{}{}.svg'.format(path, filename, i)), format='svg', dpi=1200)
            plt.savefig(str('{}/png/{}{}.png'.format(path, filename, i)), dpi=100)
            plt.clf()

            html_content.append("""
            <a download="{1}{2}.png" href="{0}/png/{1}{2}.png" title="{2}">
            <img src="{0}/svg/{1}{2}.svg" title="Click to download" alt="image not found"/></a><br>
            <figcaption class="caption">{3}</figcaption>
            """.format(path, filename, i, txt))

    return html_content

def get_linear(df):
    """Following function plots a Linear graph with line of best
    fit where the ping is a function of time for all the addresses
    and a Linear graph with line of best fit for each address.
    The Linear graph can be customized with the lin_const in the config."""

    filename = "Linear_of_"
    df.sort_values(
        by=["ip_address", "value"]
    )

    df1 = df[df["value"] > 0]

    x = df1.index
    y = df1['value']

    (a, b), _ = optimize.curve_fit(
        lambda t, a, b: a * x + b, x, y, p0=(0, 0))

    yp = a * x + b

    i = "addresses"
    plt.plot(pd.to_datetime(df1.index, unit='s'), y, "r.", label="Observations")
    plt.plot(pd.to_datetime(df1.index, unit='s'), yp, "b", label="Linear approximation")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.ylabel("Ping Values [s]")
    plt.xticks(rotation=45)
    plt.title("All addresses")
    plt.legend()
    plt.tight_layout()
    plt.savefig(str('{}/svg/{}{}.svg'.format(path, filename, i)), format='svg', dpi=1200)
    plt.savefig(str('{}/png/{}{}.png'.format(path, filename, i)), dpi=100)
    plt.clf()

    html_content = ["<h2>Linear graph<br>(Ping as a function of time)</h2>"]
    html_content.append("""
    <a download="{1}{2}.png" href="{0}/png/{1}{2}.png" title="{2}">
    <img src="{0}/svg/{1}{2}.svg" title="Click to download" alt="image not found"/></a>
    """.format(path, filename, i))


    for address in df["ip_address"].unique():
        df1 = df[df["value"] > 0]
        subset = df1[df1["ip_address"] == address]
        x = subset.index
        y = subset['value']
        if len(x) > lin_const:

            (a, b), _ = optimize.curve_fit(
                lambda t, a, b: a * x + b, x, y, p0=(0, 0))
            yp = a * x + b
            i = address

            plt.title(address)
            plt.plot(pd.to_datetime(subset.index, unit='s'), y, "r.", label="Observations")
            plt.plot(pd.to_datetime(subset.index, unit='s'), yp, "b", label="Linear approximation")
            plt.ylabel("Ping Values [s]")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(str('{}/svg/{}{}.svg'.format(path, filename, i)), format='svg', dpi=1200)
            plt.savefig(str('{}/png/{}{}.png'.format(path, filename, i)), dpi=100)
            plt.clf()

            html_content.append("""
            <a download="{1}{2}.png" href="{0}/png/{1}{2}.png" title="{2}">
            <img src="{0}/svg/{1}{2}.svg" title="Click to download" alt="image not found"/></a>
            """.format(path, filename, i))

    return html_content

def get_bar(df):
    """Following function plots a Stacked bar graph where the bars
    represent the percentage of the successful pings and unsuccessful
    pings. The count value is also shown on the bars.
    The Bar graph can be customized with the percentage_digits in the config."""

    filename = "Bar_chart"
    df.sort_values(
        by=["ip_address", "value"]
    )
    for address in df["ip_address"].unique():

        subset = df[df["ip_address"] == address]
        count_all = subset['value'].shape[0]
        count_online = subset[subset["value"] > 0].shape[0]
        ratio = round(count_online / count_all * 100, percentage_digits)
        p1 = plt.barh(address, ratio, 0.7, color="lightskyblue", label= "online")
        p2 = plt.barh(address, 100-ratio, 0.7, left=ratio, color="salmon", label= "offline")
        plt.bar_label(p1, labels=["{} ({}%)".format(count_online, ratio),], label_type='center')
        if count_all - count_online > 0:
            plt.bar_label(p2, labels=["{} ({}%)".format(count_all - count_online, round(100 - ratio, percentage_digits)), ], label_type='edge')
    plt.ylabel("Addresses")
    plt.xlabel("Percentage [%]")
    plt.title("Online and offline counts")
    plt.legend(["online", "offline"], bbox_to_anchor=(0.8, 1))
    plt.tight_layout()
    plt.savefig(str('{}/svg/{}.svg'.format(path, filename)), format='svg', dpi=1200)
    plt.savefig(str('{}/png/{}.png'.format(path, filename)), dpi=100)


    html_content = ["<h2>Stacked bar graph<br>(Successful pings and failures)</h2>"]
    html_content.append("""
    <a download="{1}.png" href="{0}/png/{1}.png" title="{1}">
    <img src="{0}/svg/{1}.svg" title="Click to download" alt="image not found"/></a>
    """.format(path, filename))

    return html_content



def get_warning_color(value):
    """Setting up the ranges provided in the config."""
    warning_colors = {
            "green": {
            "min": 0,
            "max": 90
        },
            "orange": {
            "min": 90,
            "max": 500
        },
            "red": {
            "min": 500,
            "max": 10000
        }
    }
    for key, ranges in warning_colors.items():
        if ranges["min"] < value <= ranges["max"]:
            return key
    return "black"


# # TODO should be refactored when table of server information exists
# server_info = config["server_info"]

# warning_colors = map_settings["warning_colors"]
# default_color = map_settings["default_color"]
# round_digits = int(map_settings["round_digits"])
# OPEN_BROWSER = map_settings["open_browser"]
#

def get_map(data, user_lat, user_lon):
    # making the map, center according to users location
    my_map = folium.Map(
        location=(user_lat, user_lon),
        zoom_start=2,
        max_bounds=True,
        min_zoom=2
    )

    folium.Marker(
        location=(user_lat, user_lon),
        tooltip="User",
        icon=folium.Icon(prefix="fa", icon="circle", color="gray")
    ).add_to(my_map)

    for values in data:
        city = values["location"]
        latitude = values["latitude"]
        longitude = values["longitude"]
        average_ping = round(values["average"], 2)
        address = values["ip_address"]

        tooltip = """
        <table>
          <tr>
            <td>Address:</td>
            <td><b>{}</b></td>
          </tr>
          <tr>
            <td>Median ping:</td>
            <td><b>{}</b></td>
          </tr>
        </table>
        """.format(address, average_ping)

        folium.Marker(
            location=(latitude, longitude),
            popup=city,
            tooltip=tooltip,
            icon=folium.Icon(prefix="fa", icon="circle")
        ).add_to(my_map)

        folium.PolyLine(locations=[(float(user_lat), float(user_lon)), (float(latitude), float(longitude))],
                        color=get_warning_color(average_ping),
                        weight=2,
                        opacity=0.7).add_to(my_map)

    return my_map._repr_html_()





path = "media"
hist_const = 100
hist_outlier = 0.98
round_digits = 4
lin_const = 40
percentage_digits = 2

Path(path).mkdir(exist_ok=True)
Path("{}/svg".format(path)).mkdir(exist_ok=True)
Path("{}/png".format(path)).mkdir(exist_ok=True)
