#!/usr/bin/python3
# -*- coding: utf-8 -*-

import git
import os
import shutil
import argparse
import rdflib
from rdflib.namespace import RDF
from pprint import pprint
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
from string import Template
import re



RES_DIR = './FAIRMetrics_Gen2_Code'
TEMP_DIR = './temp_dir'
RE_PATTERN_PREFIX = r'prefix ([a-z]*:) (<.*?>)'


def cloneRepo():
    git.Repo.clone_from('https://github.com/FAIRMetrics/Metrics.git', TEMP_DIR)

def getGen2MaturityIndicatorsCode():
    try:
        shutil.copytree(TEMP_DIR + '/MetricsEvaluatorCode/Ruby/metrictests', RES_DIR)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

def removeDir(dir):
    try:
        shutil.rmtree(dir)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not deleted. Error: %s' % e)

def listDirFiles(dir):

    files_list = os.listdir(dir)
    ret_files_list = []
    for file in files_list:
        try:
            g = rdflib.ConjunctiveGraph()
            result = g.parse(RES_DIR + "/" + file, format='trig')
            if file.startswith("Gen2"):
                ret_files_list.append(file)
        except rdflib.plugins.parsers.notation3.BadSyntax:
            pass
    sortFAIRList(ret_files_list)
    return ret_files_list


if __name__ == "__main__":
    if not os.path.isdir(TEMP_DIR):
        cloneRepo()

    if os.path.isdir(RES_DIR):
        removeDir(RES_DIR)

    getGen2MaturityIndicatorsCode()

    if os.path.isdir(TEMP_DIR):
        removeDir(TEMP_DIR)

    files_list = os.listdir(RES_DIR)
    print(files_list)

    tab_result = ""
    for filename in files_list:
        with open(RES_DIR + "/" + filename, "r") as f:

            if not filename.startswith("gen2_"):
                continue

            print("\n")
            print(filename)


            res_list = []
            principle = ""
            title = ""
            for line in f.read().split("\n"):

                if ":applies_to_principle =>" in line:
                    result = re.search(':applies_to_principle => (.*),', line)
                    print(result.group(1))
                    principle = result.group(1)

                if ":title =>" in line:
                    result = re.search(':title => (.*),', line)
                    print(result.group(1).replace("FAIR Metrics Gen2 - ", ""), end=" - ")
                    title = result.group(1).replace("FAIR Metrics Gen2 - ", "")
                    title = result.group(1).replace("FAIR Metrics Gen2- ", "")

                if "FAILURE" in line:
                    result = re.search('("FAILURE: (.*)")', line)
                    print(result.group(1))
                    res_list.append(result.group(1))

                if "SUCCESS" in line:
                    result = re.search('("SUCCESS: (.*)")', line)
                    print(result.group(1))
                    res_list.append(result.group(1))



            for res in res_list:
                tab_result += principle + "\t" + title + "\t" + res + "\n"


    print(tab_result)
    f = open("fm_result_comment_code.txt", "w")
    f.write(tab_result)
    f.close()
