#!/usr/bin/python3
# -*- coding: utf-8 -*-

import rdflib
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib.parse
from bs4 import BeautifulSoup
import extruct
from extruct.jsonld import JsonLdExtractor
from selenium import webdriver
import re

from pprint import pprint
from tqdm import tqdm
import time
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
TIMEOUT = (10, 300)
MAX_DOIS_PER_FILE = 5
URL_WITH_RDF = {}
DEPTH_LIMIT = 3

def retrieveWebRDF(base_url, list_tested=[], depth=-1):
    # if base_url.endswith('/'):
    #     base_url = base_url[:-1]

    page = getPage(base_url)
    html = page.content
    headers_content_type = page.headers.get('content-type')
    print("################################################")
    print(headers_content_type)


    data = {}

    if headers_content_type:
        if not "text/html" in headers_content_type: return data

    depth += 1
    if depth > DEPTH_LIMIT and DEPTH_LIMIT != 0: return data
    print("***DEPTH: " + str(depth) + "***")

    if base_url not in list_tested:
        data = rdfFromHTML(html, base_url)

    # driver = webdriver.Chrome()
    # driver.get(base_url)
    # print(driver.page_source)

    if DEPTH_LIMIT == 0: return data

    url_list = get_urls(html, base_url)

    # print(url_list)
    # print(list_tested)
    if url_list != []:
        for url in url_list:
            if not url: continue

            # if url.endswith('/'):
            #     url = url[:-1]

            # create the full url
            full_url = urllib.parse.urljoin(base_url, url)
            if full_url not in list_tested:

                list_tested.append(full_url)
                full_page = getPage(full_url)
                full_html = full_page.content
                data_sub = rdfFromHTML(full_html, full_url)

                retrieveWebRDF(full_url, list_tested, depth)
    # print(list_tested)

    return data

def getPage(base_url):
    while True:
        try:
            page = requests.get(base_url, timeout=TIMEOUT, verify=False, allow_redirects=True)
            break
        except requests.exceptions.SSLError as err:
            print(base_url)
            print(err)
            # print("Error, retrying...")
            # temp fix, should change
            # break
            time.sleep(5)
        except requests.exceptions.Timeout:
            print(base_url)
            print(err)
            print("Timeout error, retrying...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as err:
            print(base_url)
            print(err)
            print("Connection error, retrying in 60 sec...")
            time.sleep(20)

    return page

def rdfFromHTML(html, base_url):
    data = extruct.extract(html, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')


    print("URL: [" + base_url + "]")
    # print(html)
    # print(json.dumps(data, indent=2))
    for type_key in data.keys():
        # print(type_key)


        # list of namespaces
        ns_list = getRdfNameSpaces(data[type_key])

        if data[type_key] != []:
            print(type_key + " Found !")



        # if data[type_key] != []:
        if not base_url in URL_WITH_RDF.keys():
            URL_WITH_RDF[base_url] = {}
        URL_WITH_RDF[base_url][type_key] = ns_list
    print("")

    return data

def getRdfNameSpaces(elem):
    res = []
    namespaces = []
    if elem != []:
        json_str = json.dumps(elem)
        # print(json_str)
        g = rdflib.Graph()
        result = g.parse(data=json_str, format='json-ld')

        # print(len(result))
        try:
            rdf_string = g.serialize(format="turtle").decode("utf-8")
        except Exception as err:
            print(err)

        # res = g.parse(data=rdf_string, format='turtle')
        for ns in g.namespaces():
            # print(ns)
            # print(ns[1])
            if ns[0].startswith('ns'):
                namespaces.append(ns[1])
    return namespaces

def writeRdfTSV():
    f = open("rdf_webfinder_res_depth_3.tsv", "w")
    # write header
    f.write('"URL"\t"microdata"\t"json-ld"\t"rdfa"\n')
    for url in URL_WITH_RDF.keys():
        row = '"' + url + '"'
        for type_key in URL_WITH_RDF[url].keys():
            value = '"'
            for namespace in URL_WITH_RDF[url][type_key]:
                value += namespace + '\n'
            value = value.rstrip('\n')
            value += '"'
            row += '\t' + value
        row += '\n'
        f.write(row)



    f.close()

def get_urls(html, url):
    url_list = []
    if not url: return url_list

    # if url.endswith('/'):
    #     url = url[:-1]

    soup = BeautifulSoup(html, "html5lib")
    # for link in soup.findAll('a'):
    #     print(link.get('href'))

    # for link in soup.findAll('a'):
    ignore_ext_list = [
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "gz",
        "svg",
        "jptb1m"
    ]
    for link in soup.findAll('a', attrs={'href': re.compile("^/")}):
        if link.get('href').split(".")[-1] in ignore_ext_list: continue
        url_list.append(link.get('href'))
        # print(link.get('href'))


    return url_list

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

    uniprot_url = "https://www.uniprot.org/uniprot/P04637"
    # uniprot_url = "https://www.uniprot.org/uniprot/P38398"

    rir_elixir = [
        "https://biit.cs.ut.ee/gprofiler/gost", # javascript generated
        "https://identifiers.org/", # javascript generated
        # "https://fairsharing.org/", # json-ld schema.org
        # "https://fairsharing.org/collection/ComputationalModeling",
        # "https://fairsharing.org/recommendation/ScientificData",
        "http://intermine.org/", #rdfa basique w3.org
        "https://isa-tools.org/", #rdfa basique w3.org
        "https://www.ebi.ac.uk/ols/index", #rdfa avec https://ogp.me/ onto
        "https://3dbionotes.cnb.csic.es/ws/api", # rien du tout
        # "https://www.bridgedb.org/", # CertificateError tester ouverture navigateur
        "https://www.disgenet.org/rdf", # rien du tout
        "https://molgenis.github.io/", #rdfa basique w3.org
        "https://fair-dom.org/platform/seek/", # rdfa w3.org
        "https://dev.workflowhub.eu",



    ]

    # list_tested = []
    for ressource_url in rir_elixir:
        # print("------------------------------------------------")
        # print("URL: [" + ressource_url + "]")
        res_rdf = retrieveWebRDF(ressource_url)
        # for type_key in res_rdf.keys():
        #     print(type_key)
        #     # print(json.dumps(res_rdfa[type_key], indent=2))
        #     for res in res_rdf[type_key]:
        #         if "@context" in res.keys():
        #             print("@context: " + res["@context"])
        #         else:
        #             print(res)
        #
        #         if "@type" in res.keys():
        #             print("@type: " + res["@type"])
        #
        #     print("")

    print(json.dumps(URL_WITH_RDF, indent=4))
    writeRdfTSV()
    sys.exit(0)

    time.sleep(10)

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
            json_ld = retrieveWebRDF(url)["json-ld"]

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
