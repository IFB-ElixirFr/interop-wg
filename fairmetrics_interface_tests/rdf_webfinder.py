#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
from extruct.jsonld import JsonLdExtractor
from pprint import pprint
from tqdm import tqdm
import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams


TIMEOUT = (10, 300)
MAX_DOIS_PER_FILE = 400

def retrieveWebJSONLD(url):

    while True:
        try:
            page = requests.get(url, timeout=TIMEOUT)
            break
        except requests.exceptions.SSLError as err:
            print(url)
            print(err)
            # print("Error, retrying...")
            # temp fix, should change
            # break
            time.sleep(5)
        except requests.exceptions.Timeout:
            print(url)
            print(err)
            print("Timeout error, retrying...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as err:
            print(url)
            print(err)
            print("Connection error, retrying in 60 sec...")
            time.sleep(20)


    html = page.content

    jslde = JsonLdExtractor()

    data = jslde.extract(html)
    # pprint(data)
    return data

def readDOIsFile(filename):
    """
    Read the DOIs from a file input.

    @param filename String The inputs DOIs to be tested
    """
    with open(filename, 'r') as file:
        data = file.read()
    return data

def generateBarPlot(properties, count):
    # dataset:
    height = count
    bars = properties

    # Set label and title
    fig, ax = plt.subplots()
    ax.set_ylabel('Count')
    ax.set_xlabel('Properties')
    ax.set_title('Count of Schema.org/Dataset properties')
    plt.figure(figsize=(20,14))

    rcParams.update({'figure.autolayout': True})
    y_pos = np.arange(len(bars))

    # Create bars
    plot_bars = plt.bar(y_pos, height)

    # Create names on the x-axis
    plt.xticks(y_pos, bars, rotation=60, ha="right")

    # access the bar attributes to place the text in the appropriate location
    for bar in plot_bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height / 2., "%d" % height, ha="center", va="center", fontweight="bold")

    plt.savefig("res1.png")
    # Show graphic
    plt.show()

def stackedBarPlot(total_property_count, dict_property_count):

    # Set label and title
    fig, ax = plt.subplots()
    ax.set_ylabel('Count')
    ax.set_xlabel('Properties')
    ax.set_title('Count of Schema.org/Dataset properties')
    plt.figure(figsize=(20,14))

    rcParams.update({'figure.autolayout': True})

    names = sorted(total_property_count.keys())
    r = np.arange(len(total_property_count.keys()))
    # Create names on the x-axis
    plt.xticks(r, names, rotation=60, ha="right")

    for key in total_property_count.keys():
        for dict_key in dict_property_count.keys():
            dict = dict_property_count[dict_key]
            if not key in dict.keys(): dict[key] = 0

    list_list_count = []
    bars_list = []
    # r = range(len(total_property_count.keys()))
    index = 0
    for dict_key in dict_property_count.keys():
        dict = dict_property_count[dict_key]
        list_count = []
        for key in sorted(dict.keys()):
            list_count.append(dict[key])

        # print(list_count)
        if index == 0:
            bars_list.append(plt.bar(r, list_count, edgecolor='white'))
        else:
            numpy_array = np.array(list_list_count)
            bottom = np.sum(numpy_array, 0).tolist()
            bars_list.append(plt.bar(r, list_count, bottom=bottom, edgecolor='white'))
        list_list_count.append(list_count)
        index += 1

    for bars in bars_list:
        for bar in bars:
            # Value in rectangle
            height = bar.get_height()
            if height == 0: continue

            # Position
            position = bar.get_y() + height / 2.

            plt.text(bar.get_x() + bar.get_width() / 2., position, "%d" % height, ha="center", va="center", fontweight="bold")

    plt.legend(bars_list, dict_property_count.keys())



    plt.savefig("res_stacked1.png")
    # Show graphic
    plt.show()


if __name__ == "__main__":

    url = "https://data.inra.fr/dataset.xhtml?persistentId=doi:10.15454/HAEY8H"
    url = "https://zenodo.org/record/3727291#.XnzkZKHPyUk"
    url = "https://doi.pangaea.de/10.1594/PANGAEA.109987"
    url = "https://datadryad.org/stash/dataset/doi:10.5061/dryad.8962"


    filename_list = [
        "./input/inrae_dataverse_dataset_dois.txt",
        "./input/pangaea_dataset_dois.txt",
        "./input/zenodo_dataset_dois.txt",
        "./input/dryad_dataset_dois.txt",
    ]


    total_property_count = {}
    dict_property_count = {}

    # for each file in list
    for filename in filename_list:
        url_list = readDOIsFile(filename).split("\n")
        url_sublist = url_list[0:MAX_DOIS_PER_FILE]

        property_count = {}

        print("Counting properties for file: [" + filename + "]")
        # for each url in file
        for url in tqdm(url_sublist, total=MAX_DOIS_PER_FILE):

            # get json ld
            json_ld = retrieveWebJSONLD(url)

            try:
                exist = json_ld[0]
            except IndexError:
                continue

            if "schema.org" not in json_ld[0]['@context']: continue
            if not json_ld[0]['@type'].lower() == 'dataset': continue
            # property_counter
            for key in json_ld[0].keys():
                if key not in property_count.keys():
                    property_count[key] = 1
                else:
                    property_count[key] += 1

                if key not in total_property_count.keys():
                    total_property_count[key] = 1
                else:
                    total_property_count[key] += 1
                # print(key)
        print(json.dumps(property_count, indent=4))
        new_key = filename.split("/")[-1]
        dict_property_count[new_key] = property_count
        properties = property_count.keys()
        count = property_count.values()
        # generateBarPlot(properties, count)

    print("\nTotal:\n")
    print(json.dumps(total_property_count, indent=4))

    stackedBarPlot(total_property_count, dict_property_count)

    properties = sorted(total_property_count.keys())
    count = [total_property_count[property] for property in properties]
    generateBarPlot(properties, count)
