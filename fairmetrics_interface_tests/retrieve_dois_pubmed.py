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

import re
# xml parser
import xml.etree.ElementTree as ET
# from lxml import etree as ET

import requests

# timeout (connect, read) in secondes
TIMEOUT = (10, 300)

"""
Pour installer E-Direct:

cd ~
/bin/bash
perl -MNet::FTP -e \
    '$ftp = new Net::FTP("ftp.ncbi.nlm.nih.gov", Passive => 1);
    $ftp->login; $ftp->binary;
    $ftp->get("/entrez/entrezdirect/edirect.tar.gz");'
gunzip -c edirect.tar.gz | tar xf -
rm edirect.tar.gz
builtin exit
export PATH=${PATH}:$HOME/edirect >& /dev/null || setenv PATH "${PATH}:$HOME/edirect"
./edirect/setup.sh
"""

def globalESEF(min_date, max_date, term):
    """
    @param term The geo request terms
    @param mindate mindate from when retrieve publications (YYYY/MM/DD)
    @param maxdate maxdate from when retrieve publications (YYYY/MM/DD)

    @return xml_root containing all requests results
    """

    # print('Retrieving data from ' + mindate + ' to ' + maxdate)
    # print('Terms :' + term + '\n')

    while(True):
        # command line for edirect
        command = "esearch -db pubmed -query " + term + " -datetype pdat -mindate " + min_date + " -maxdate " + max_date + " | efetch -format docsum"
        print(command, end="\n\n")
        completed_proc = subprocess.Popen(command, shell=True, stdout=PIPE)
        result, error = completed_proc.communicate()
        result = result.decode("utf-8")
        result = xmlMultiRootCleaner(result)

        result = result.replace('&rsquo;', ' ')
        result = re.sub(r'&', '&amp;', result)
        res = result.split('\n')

        try:
            parser = ET.XMLParser(encoding="utf-8")
            # xml result
            xml_root = ET.fromstring(result, parser=parser)
            print('EDirect request succeded !\n')
            break
        except ET.ParseError as e:
            print('EDirect request failed, retrying...\n')
            print(e)
            time.sleep(10)
    return xml_root


def xmlMultiRootCleaner(result):
    """
    Clean xml: big xml returned by esearch/efetch has multiples roots and cant be parsed

    @param result xml from first EDirect esearch/efetch
    """
    num_lines = sum(1 for line in result.splitlines())
    accumulated_xml = []
    lines = result.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('<?xml') and i != 0:
            pass
        elif line.startswith('<!DOCTYPE') and i != 1:
            pass
        elif line.startswith('<DocumentSummarySet status=') and i != 3:
            pass
        elif line.startswith('</DocumentSummarySet') and i != num_lines-2:
            pass
        else:
            accumulated_xml.append(line)
    accumulated_xml = '\n'.join(accumulated_xml)
    return accumulated_xml


def getDOISFromXML(xml_root):

    dois_list = []
    # print(xml_root)
    for docsums in xml_root.iter('DocumentSummary'):
        for article_ids in docsums.findall('ArticleIds'):
            for article_id in article_ids.findall('ArticleId'):
                for id_type in article_id.findall('IdType'):
                    if id_type.text == 'doi':
                        for value in article_id.findall('Value'):
                            dois_list.append(value.text)
    return dois_list

def convertPMIDtoDOI(url_test):
    """

    """
    # url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=" + ids + "&format=json"
    response = requests.request(method='GET', url=url_test, timeout=TIMEOUT)

    result = response.json()
    print(result)
    return result

def writeDOIs(dois_list, min_date, max_date, term):
    term = term.replace(" ", "_")
    min_date = min_date.replace("/", "_")
    max_date = max_date.replace("/", "_")
    path = os.getcwd() + "/" + term
    if not os.path.isdir(path):
        os.mkdir(path)
    filename = term + "-" + min_date + "-" + max_date + ".txt"
    dois = '\n'.join(dois_list)
    output = open(path + "/" + filename, 'w')
    output.write(dois)
    output.close
    print("Result available in [" + path + "/" + filename + "]")

if __name__ == "__main__":
    url_test = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=23193287&format=json"

    term = "bioinformatics"
    min_date = "2018/06/02"
    max_date = "2018/06/10"
    xml_root = globalESEF(min_date, max_date, term)
    dois_list = getDOISFromXML(xml_root)

    print("Total number of DOIs found: " + str(len(dois_list)), end="\n\n")
    writeDOIs(dois_list, min_date, max_date, term)
