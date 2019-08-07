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
NB = '5000'
OUTPUT_DIR = "input"

def dryadRequest():
    print("REST request to dryad...")
    # rest request
    url = 'http://api.datadryad.org/mn/object?count=' + NB
    while True:
        try:
            response = requests.get(url, timeout=TIMEOUT)
            break
        except SSLError:
            print("Error, retrying...")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("Timeout error, retrying...")
            time.sleep(5)

    return response.text

def dryadResponseToXML(response):
    print("Parsing result...")
    while True:
        try:
            parser = ET.XMLParser(encoding="utf-8")
            # xml result
            xml_root = ET.fromstring(response, parser=parser)
            break
        except ET.ParseError as e:
            print(e)
            time.sleep(10)

    return xml_root

def dryadXMLParser(xml_root):
    dois_list = []

    for object_info in xml_root.iter('objectInfo'):
        for identifier in object_info.findall('identifier'):
            dois_list.append(identifier.text.split('?')[0])
    dois_list = list(set(dois_list))
    return dois_list

def writeDOIs(dois_list):
    print("Writing result...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/dryad_dataset_dois.txt"
    dois = '\n'.join(dois_list)
    output = open(filename, 'w')
    output.write(dois)
    output.close

if __name__ == "__main__":
    response = dryadRequest()
    xml_root = dryadResponseToXML(response)
    dois_list = dryadXMLParser(xml_root)
    writeDOIs(dois_list)
