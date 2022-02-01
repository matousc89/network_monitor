"""Data Analysis

This script provides some data analysis for the given data.

The user can customize some of the graph parameters in the config.

This script requires that `matplotlib`, `pandas`, `scipy` and
`webbrowser` be installed within the Python environment you are
running this script in.

"""

import json
import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
import webbrowser

from storages.engines import get_reader_engine



def convert_xlsx2csv(source, target):
    """ Convert excel file to csv. """
    pd.read_excel(source).to_csv(target, index=False)


def get_histogram(df):
    """Following function plots a Histogram representing the distribution
    of pings for all the addresses and a Histogram for each address.
    The Histogram can be customized with the parameters in the config."""

    filename = "Histogram_of_"
    df.sort_values(
        by=["address", "value"]
    )
    for address in df["address"].unique():
        df1 = df[df["value"] > 0]
        subset = df1[df1["address"] == address]
        subset = subset[subset["value"] < subset["value"].quantile(hist_outlier)]
        if len(subset) > hist_const:
            bins = min(100, len(subset) // 10)
            i = "addresses"
            subset['value'].hist(bins=bins,
                                  histtype='step'
                                  )

    plt.legend(df1["address"])
    plt.xlabel("Ping Values [s]")
    plt.ylabel("Number of occurrences")
    plt.title("Distribution of Ping Values")
    plt.savefig(str('{}/svg/{}{}.svg'.format(path, filename, i)), format='svg', dpi=1200)
    plt.savefig(str('{}/png/{}{}.png'.format(path, filename, i)), dpi=100)
    plt.clf()


    html_content = ["<h2>Histograms<br>(Distribution of pings)</h2>"]
    html_content.append("""
    <a download="{1}{2}.png" href={0}/png/{1}{2}.png" title="{2}">
    <img src="{0}/svg/{1}{2}.svg" title="Click to download" alt="image not found"/><br>
    """.format(path, filename, i))


    for address in df["address"].unique():

        subset_all = df[df["address"] == address]
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
        by=["address", "value"]
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


    for address in df["address"].unique():
        df1 = df[df["value"] > 0]
        subset = df1[df1["address"] == address]
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
        by=["address", "value"]
    )
    for address in df["address"].unique():

        subset = df[df["address"] == address]
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

def build_html(html_content):
    """Following function builds the index.html file using the html template and
    the html_str.
    html_content is appended after each graph."""

    html_str = "\n".join(html_content)

    with open("template.html", "r") as f:
        html = f.read()

    html = html.replace("[[ content ]]", str(html_str))

    with open("index.html", "w") as f:
        f.write(html)


def open_local_file():
    """Opening the html file in a browser."""
    webbrowser.open('file://' + os.path.realpath("index.html"))

with open("config.json", "r") as f:
    config = json.loads(f.read())

storage_engine = get_reader_engine(config["writer_settings"]["engine"])
graph_settings = config["graph_settings"]
path = graph_settings["path"]
hist_const = int(graph_settings["hist_const"])
hist_outlier = float(graph_settings["hist_outlier"])
round_digits = int(graph_settings["round_digits"])
lin_const = int(graph_settings["lin_const"])
percentage_digits = int(graph_settings["percentage_digits"])
OPEN_BROWSER = graph_settings["open_browser"]
dfs = storage_engine.get_tables()
df = dfs["ping"]
Path(path).mkdir(exist_ok=True)
Path("{}/svg".format(path)).mkdir(exist_ok=True)
Path("{}/png".format(path)).mkdir(exist_ok=True)



html_content = []

html_content += get_histogram(df)
html_content += get_linear(df)
html_content += get_bar(df)

build_html(html_content)

if OPEN_BROWSER:
    open_local_file()
