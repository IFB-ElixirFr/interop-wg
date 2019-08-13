#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime

import re
# xml parser
import xml.etree.ElementTree as ET
# from lxml import etree as ET

import requests

# timeout (connect, read) in secondes
TIMEOUT = (10, 300)
MAX_NB = 200
OUTPUT_DIR = "input"

def biotoolsRestRequest(page):
    print("REST request to biotools...")
    print(page)
    # rest request
    url = 'https://bio.tools/api/tool/?format=json&q=rsat&' + page[1:]
    while True:
        try:
            response = requests.get(url, timeout=TIMEOUT)
            json_response = response.json()
            break
        except SSLError:
            time.sleep(5)
        except requests.exceptions.Timeout:
            time.sleep(5)
    return json_response

def biotoolsJsonParser(json_response, dois_list, biotools_id_list):
    print("Parsing result...")

    for element in json_response["list"]:
        if element["publication"] != []:
            for publication in element["publication"]:
                doi = publication["doi"]
                # avoid null/None doi
                if doi:
                    dois_list.append(doi)

        if element["biotoolsID"]:
            biotools_id_list.append(element["biotoolsID"])


    if json_response["next"] and len(dois_list) < MAX_NB:
        json_response = biotoolsRestRequest(json_response["next"])
        biotoolsJsonParser(json_response, dois_list, biotools_id_list)

    return dois_list, biotools_id_list

def writeDOIs(dois_list):
    print("Writing result...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/biotools_dataset_dois.txt"
    dois = '\n'.join(dois_list)
    output = open(filename, 'w')
    output.write(dois)
    output.close

def writeIdentifiers(biotools_id_list):
    print("Writing Identifiers...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/biotools_dataset_identifiers.txt"

    for i, element in enumerate(biotools_id_list):
        biotools_id_list[i] = "https://identifiers.org/biotools:" + element

    identifiers = '\n'.join(biotools_id_list)
    output = open(filename, 'w')
    output.write(identifiers)
    output.close

if __name__ == "__main__":
    page = "?page=1"
    dois_list = []
    biotools_id_list = []
    json_response = biotoolsRestRequest(page)
    dois_list, biotools_id_list = biotoolsJsonParser(json_response, dois_list, biotools_id_list)
    writeDOIs(dois_list)
    writeIdentifiers(biotools_id_list)
