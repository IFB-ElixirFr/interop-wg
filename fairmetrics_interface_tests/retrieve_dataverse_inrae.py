#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
import os


# timeout (connect, read) in secondes
TIMEOUT = (10, 300)
# NB = '5000'
OUTPUT_DIR = "input"

def writeDOIs(dois_list):
    print("Writing result...")
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    filename = OUTPUT_DIR + "/inrae_dataverse_dataset_dois.txt"
    dois = '\n'.join(dois_list)
    output = open(filename, 'w')
    output.write(dois)
    output.close

def inraeRequest(url):
    while True:
        try:
            page = requests.get(url, timeout=TIMEOUT)
            break
        except requests.exceptions.SSLError:
            print("Error, retrying...")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("Timeout error, retrying...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as err:
            print(err)
            print("Connection error, retrying in 60 sec...")
            time.sleep(60)
    return page

if __name__ == "__main__":

    base = 'https://data.inra.fr/'
    type = "dataset"
    rows = 1
    start = 0
    page = 1
    condition = True # emulate do-while
    dois_list = []

    while (condition):
        url = base + '/api/search?q=*' + "&start=" + str(start) + "&type=" + str(type) + "&per_page=" + str(rows)
        data = inraeRequest(url).json()
        total = data['data']['total_count']
        print("=== Page" + str(page) + "===")
        print("start:" + str(start) + " total:" + str(total))
        for i in data['data']['items']:
            print("- " + i['name'] + "(" + i['url'] + ")")
            dois_list.append(i['url'])
        start = start + rows * 50
        page += 1
        condition = start < total

        # stop after 100 dois
        if page == 1001:
            break

    writeDOIs(dois_list)
