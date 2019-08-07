#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import urllib
import urllib.request
import json
import requests
from requests.exceptions import SSLError
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
TIMEOUT = (10, 28800)
PRINT_DETAILS = False

def animated_loading(message):
    """
    Add an animated character to show loading at the end of a message.

    @param message String The message to be displayed
    """

    # string of char the will be displayed in a loop
    chars = "/—\|"

    # the loop over the chars
    for char in chars:
        sys.stdout.write('\r' + message + char)
        time.sleep(.1)
        sys.stdout.flush()

def processFunction(function, args, message):
    """
    The function that execute another function through a wrapper allowing for an animated message while executed.

    @param function Method A python function to be executed
    @param args List The arguments of the function to be executed
    @param message String The message to be displayed
    """

    # List that will contains the results of the input function
    res = []
    # Initialize and start the process
    the_process = threading.Thread(target=wrapper, args=(function, args, res))
    the_process.start()

    # Execute the animated message as long as the process is alive (executing the input function)
    if PRINT_DETAILS:
        while the_process.isAlive():
            animated_loading(message)

    the_process.join()

    # print('test')
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

    return res[0]

def wrapper(func, args, res):
    """
    The wrapper that execute the input function.

    @param func Method The python function to be executed
    @param args List The arguments of the function to be executed
    @param res List The list of results from the input function
    """
    res.append(func(*args))

def testMetric(metric_api_url, data):
    """
    Send a request to the URL api that will test the metric.

    @param metric_api_url String The URL of one metric to test the data against
    @param data dict Contain the GUID to be tested

    @return json Result returned by the request that is JSON-LD formated
    """
    while True:
        try:
            response = requests.request(method='POST', url=metric_api_url, data=data, timeout=TIMEOUT)
            result = response.json()
            break
        except requests.exceptions.Timeout:
            print("Timeout, retrying...")
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            print("ReadTimeout, retrying...")
            time.sleep(20)
        except SSLError:
            print("SSLError, retrying...")
            time.sleep(10)

    return result


def testMetrics(GUID):
    """
    Call multiples time "testMetric" to test each metric against one GUID.

    @param GUID String The GUID to be tested
    """

    # Create the data dict containing the GUID
    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    # Retrieve all the metrics general info and api urls
    metrics = getMetrics()

    # list that will contains the score for each metric test
    test_line_list = [GUID]
    # list that will contains the name of each (principle) metric test (F1, A1, I2, etc)
    headers_list = ["GUID"]

    n = 0

    # iterate over each metric
    for metric in metrics:
        n += 1

        # retrieve more specific info about each metric
        metric_info = processFunction(getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
        # retrieve the name (principle) of each metric (F1, A1, I2, etc)
        principle = metric_info["principle"].rsplit('/', 1)[-1]

        # if True:
        if principle[0] == 'F':
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

            # append score and principle
            test_line_list.append(score)
            headers_list.append(principle)

    # write the list of score (and header if file doesnt exists yet) to a result file
    writeLineToFile("\t".join(test_line_list), "\t".join(headers_list), "", "result_metrics_test.tsv")

def getMetricInfo(metric_url):
    """
    Send a request to retrieve additional info about one metric.

    @param metric_url String The url where the metric informations are

    @return json Result returned by the request that is JSON-LD formated
    """
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
    """
    A function that send the comments of a metric test against a GUID to the stdout.

    @param key
    """
    print("Comment:")
    # print(result[0][key][0]['@value'], end='\n\n')
    comment_list = result[0][key][0]['@value'].split('\n')
    for line in comment_list:
        # if line.startswith('SUCCESS') or line.startswith('FAILURE'):
        l = colorComment(line)
        print(l, end='\n')

def colorComment(line):
    """
    Color some specific terms in the comments in the stdout.

    @param line String The comment line to be colored
    """

    # dict containing words as key and the associated color as value
    association_dict = {
                        'SUCCESS': 'green',
                        'FAILURE': 'red',
                        'WARN': 'yellow',
                        'INFO': 'cyan',
                        'CRITICAL': 'magenta',
                        }
    l = ''
    # add the color to the terms if they exists
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
    """
    Retrieve general informations of each metrics.

    @return json Result returned by the request that is JSON-LD formated
    """

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
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("ConnectionError, retrying...")
            time.sleep(10)

    json_res = response.json()

    return json_res

def writeLineToFile(test_line, headers_list, descriptions_list, filename):
    """
    Write a line of scores associated to a GUID to a res file, create the file and headers if it doesn't exist yet.

    @param test_line List Score results for each test (0 or 1)
    @param headers_list List Principle of each metric that will be used as headers
    @param descriptions_list List Contains the description of eache principle added to the top of the file
    @param filename String The name of the output file
    """
    logname = "result_metrics_test.log"

    exists = os.path.isfile(filename)
    if exists:
        file = open(filename, "a")
        file.write("\n" + test_line )
        file.close()
    else:
        file = open(filename, "w")
        file.write(descriptions_list)
        file.write("\n" + headers_list)
        file.write("\n" + test_line)
        file.close()

def readDOIsFile(filename):
    """
    Read the DOIs from a file input.

    @param filename String The inputs DOIs to be tested
    """
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
    # GUID_test = "https://doi.org/10.5061/dryad.615"
    GUID_test = "10.1155/2019/2561828"

    # GUID_test = "10.1002/cpbi.72"
    # GUID_test = "10.1093/neuros/nyw135"
    # GUID_test = 'https://orcid.org/0000-0002-3597-8557'
    for i in range(0, 50):
        testMetrics(GUID_test)








#curl -X POST -D -L -H "Content-Type: application/json" -H "Accept: application/json" -d '{"subject": "10.5281/zenodo.1147435"}' http://linkeddata.systems/cgi-bin/FAIR_Tests/gen2_unique_identifier
