#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import urllib
import urllib.request
import json
import requests
import rdflib
from rdflib import Graph, plugin
from rdflib.serializer import Serializer
import argparse
import termcolor

import itertools
import threading
import time
import sys

import joblib
from joblib import Parallel, delayed
import multiprocessing
from multiprocessing import Pool

from tqdm import *

from threading import *

import random

from reprint import output

import subprocess



# timeout (connect, read) in secondes
TIMEOUT = (10, 300)
PRINT_DETAILS = False
COUNT = 0

def animated_loading(message):
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r' + message + char)
        time.sleep(.1)
        sys.stdout.flush()

def processFunction(function, args, message):
    res = []
    the_process = threading.Thread(target=wrapper, args=(function, args, res))
    the_process.start()

    if PRINT_DETAILS:
        while the_process.isAlive():
            animated_loading(message)

    the_process.join()

    # print('test')
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

    return res[0]

def wrapper(func, args, res):
    res.append(func(*args))

def testMetric(metric_api_url, data):
    """

    """
    while True:
        try:
            response = requests.request(method='POST', url=metric_api_url, data=data, timeout=TIMEOUT)
            result = response.json()
            break
        except requests.exceptions.Timeout:
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            time.sleep(20)
        except SSLError:
            time.sleep(10)

    return result

def getCount():
    return COUNT

def setCount(count):
    COUNT = count

def testMetrics(GUID):
    # COUNT=0
    # COUNT += 1
    # dois_num = COUNT



    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    metrics = getMetrics()

    test_line_list = [GUID]
    headers_list = ["GUID"]

    # print(count)
    n = 0

    for metric in metrics:

        n += 1


        metric_info = processFunction(getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
        # metric_info = getMetricInfo(metric["@id"])
        principle = metric_info["principle"].rsplit('/', 1)[-1]

        # pbar.set_description('Test [' + principle + '] for [' + GUID + ']')

        if principle[0] == 'I':
            if PRINT_DETAILS:
                # print informations related to the metric
                printMetricInfo(metric_info)

            # evaluate the metric
            metric_evaluation_result = processFunction(testMetric, [metric["smarturl"], data], 'Evaluating metric... ')

            if PRINT_DETAILS:
                #print results of the evaluation
                printTestMetricComment('http://schema.org/comment', metric_evaluation_result)
                printTestMetricScore('http://semanticscience.org/resource/SIO_000300', metric_evaluation_result)

            # get the score
            score = metric_evaluation_result[0]['http://semanticscience.org/resource/SIO_000300'][0]['@value']
            score = str(int(float(score)))

            test_line_list.append(score)
            headers_list.append(principle)

    writeLineToFile("\t".join(test_line_list), "\t".join(headers_list), "result_metrics_test.tsv")

def getMetricInfo(metric_url):
    while True:
        try:
            response = requests.request(method='GET', url=metric_url + '.json', allow_redirects=True, timeout=TIMEOUT)
            result = response.json()
            break
        except requests.exceptions.Timeout:
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            time.sleep(20)
        except SSLError:
            time.sleep(10)
    return result

def printTestMetricComment(key, result):
    print("Comment:")
    # print(result[0][key][0]['@value'], end='\n\n')
    comment_list = result[0][key][0]['@value'].split('\n')
    for line in comment_list:
        # if line.startswith('SUCCESS') or line.startswith('FAILURE'):
        l = colorComment(line)
        print(l, end='\n')

def colorComment(line):
    association_dict = {
                        'SUCCESS': 'green',
                        'FAILURE': 'red',
                        'WARN': 'yellow',
                        'INFO': 'cyan',
                        }
    l = ''
    for key_term, value_color in association_dict.items():
        if line.startswith(key_term):
            l = line.replace(key_term, termcolor.colored(key_term, value_color))
            return l

    return line


def printTestMetricScore(key, result):
    print("\nScore:")
    print(result[0][key][0]['@value'], end='\n\n')

def printMetricInfo(metric_info):
    print('####################################################################', end='\n\n')
    print(metric_info["name"], end='\n\n')
    print("Principle: " + metric_info["principle"].rsplit('/', 1)[-1], end='\n\n')
    print("Description:")
    print(metric_info["description"], end='\n\n')

def getMetrics():
    metrics_url = 'https://ejp-evaluator.appspot.com/FAIR_Evaluator/metrics.json'
    while(True):
        try:
            response = requests.get(metrics_url, timeout=TIMEOUT)
            break
        except SSLError:
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("Timeout, retrying")
            time.sleep(5)

    json_res = response.json()

    return json_res

def writeLineToFile(test_line, headers_list, filename):

    logname = "result_metrics_test.log"

    exists = os.path.isfile(filename)
    if exists:
        file = open(filename, "a")
        file.write("\n" + test_line )
        file.close()
    else:
        file = open(filename, "w")
        file.write(headers_list)
        file.write("\n" + test_line)
        file.close()

def writeHeader():
    toto = "2"
    print(toto)

def readDOIsFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

if __name__ == "__main__":

    PRINT_DETAILS = True

    # RSAT paper
    # GUID_test = "10.1093/nar/gky317"

    # Dataset +++
    # GUID_test = "https://doi.pangaea.de/10.1594/PANGAEA.902591"

    # Dataset
    GUID_test = "https://doi.org/10.5061/dryad.615"

    # GUID_test = "10.1002/cpbi.72"
    # GUID_test = "10.1093/neuros/nyw135"
    # GUID_test = 'https://orcid.org/0000-0002-3597-8557'

    testMetrics(GUID_test)








#curl -X POST -D -L -H "Content-Type: application/json" -H "Accept: application/json" -d '{"subject": "10.5281/zenodo.1147435"}' http://linkeddata.systems/cgi-bin/FAIR_Tests/gen2_unique_identifier
