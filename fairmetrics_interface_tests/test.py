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


# timeout (connect, read) in secondes
TIMEOUT = (10, 300)



def testMetric(metric_api_url, data):
    """

    """

    response = requests.request(method='POST', url=metric_api_url, data=data, timeout=TIMEOUT)

    result = response.json()

    for key in result[0]:
        if key == 'http://schema.org/comment':
            print("Comment:")
            print(result[0][key][0]['@value'], end='\n\n')
        if key == 'http://semanticscience.org/resource/SIO_000300':
            print("Score:")
            print(result[0][key][0]['@value'], end='\n\n')
            score = result[0][key][0]['@value']

    print('####################################################################', end='\n\n')

    # g = Graph().parse(data=response.text, format='application/ld+json')
    # print(g.serialize(format='json-ld', indent=4))

    return str(int(float(score)))



def testMetrics(GUID):
    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    metrics = getMetrics()

    test_line_list = [GUID]
    headers_list = ["GUID"]

    for metric in metrics:
        print(metric["name"], end='\n\n')
        metric_info = getMetricInfo(metric["@id"])
        score = testMetric(metric["smarturl"], data)
        # print(metric["@id"])
        test_line_list.append(score)
        headers_list.append(metric_info["principle"].rsplit('/', 1)[-1])

    writeLineToFile("\t".join(test_line_list), "\t".join(headers_list))

def getMetricInfo(metric_url):
    response = requests.request(method='GET', url=metric_url + '.json', allow_redirects=True, timeout=TIMEOUT)
    result = response.json()

    print("Principle: " + result["principle"].rsplit('/', 1)[-1], end='\n\n')


    print("Description:")
    print(result["description"], end='\n\n')

    return result

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

def writeLineToFile(test_line, headers_list):
    filename = "result_metrics_test.tsv"
    logname = "result_metrics_test.log"

    exists = os.path.isfile('result_metrics_test.tsv')
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
    toto = ""

if __name__ == "__main__":
    # GUID_test = "10.1002/cpbi.72"
    GUID_test = "10.1093/neuros/nyw135"
    # GUID_test = 'https://orcid.org/0000-0002-3597-8557'
    print("Testing GUID: " + GUID_test, end="\n\n")
    testMetrics(GUID_test)



#curl -X POST -D -L -H "Content-Type: application/json" -H "Accept: application/json" -d '{"subject": "10.5281/zenodo.1147435"}' http://linkeddata.systems/cgi-bin/FAIR_Tests/gen2_unique_identifier
