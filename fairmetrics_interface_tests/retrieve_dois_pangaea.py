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
NB = '5000'
OUTPUT_DIR = "input"

def pangaeaRestRequest():
    print("REST request to pangaea...")
    # rest request
    url = 'https://ws.pangaea.de/es/portals/pansimple/_search?pretty&size=' + NB
    while True:
        try:
            response = requests.get(url, timeout=TIMEOUT)
            break
        except SSLError:
            time.sleep(5)
        except requests.exceptions.Timeout:
            time.sleep(5)

    return response

def pangaeaJsonParser(response):
    print("Parsing result...")
    json_response = response.json()

    dois_list = []
    for element in json_response["hits"]["hits"]:
        doi = element["_source"]["metadatalink"]
        dois_list.append(doi)

    return dois_list


def writeDOIs(dois_list):
    print("Writing result...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/pangaea_dataset_dois.txt"
    dois = '\n'.join(dois_list)
    output = open(filename, 'w')
    output.write(dois)
    output.close

if __name__ == "__main__":
    response = pangaeaRestRequest()
    dois_list = pangaeaJsonParser(response)
    writeDOIs(dois_list)
