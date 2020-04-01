#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Command line exec
import subprocess
from subprocess import Popen
from subprocess import PIPE
from subprocess import run

import os
import sys
import time
import datetime
import json

import re
# xml parser
import xml.etree.ElementTree as ET
# from lxml import etree as ET

import requests

# timeout (connect, read) in secondes
TIMEOUT = (10, 300)
NB = 1000
TYPE = "dataset"
OUTPUT_DIR = "input"

def zenodoRestRequest():
    print("REST request to zenedo...")
    # rest request
    url = 'https://zenodo.org/api/records/?sort=mostrecent&page=1&size=' + "7000"
    while True:
        try:
            response = requests.get(url, timeout=TIMEOUT)
            break
        except SSLError:
            time.sleep(5)
        except requests.exceptions.Timeout:
            time.sleep(5)

    return response

def zenodoJsonParser(response):
    print("Parsing result...")
    json_response = response.json()

    dois_list = []
    count = 1
    for element in json_response["hits"]["hits"]:
        type = element["metadata"]["resource_type"]["type"]
        if type == TYPE:
            if count > NB: break
            dois_list.append("https://doi.org/" + element["doi"])
            count += 1


    return dois_list


def writeDOIs(dois_list):
    print("Writing result...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/zenodo_dataset_dois.txt"
    dois = '\n'.join(dois_list)
    output = open(filename, 'w')
    output.write(dois)
    output.close

if __name__ == "__main__":
    response = zenodoRestRequest()
    dois_list = zenodoJsonParser(response)
    writeDOIs(dois_list)
