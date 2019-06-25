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
import termcolor


RES_DIR = './FAIRMetrics_Gen2'
TEMP_DIR = './temp_dir'
RE_PATTERN_PREFIX = r'prefix ([a-z]*:) (<.*?>)'


def cloneRepo():
    git.Repo.clone_from('https://github.com/FAIRMetrics/Metrics.git', TEMP_DIR)

def getGen2MaturityIndicators():
    try:
        shutil.copytree(TEMP_DIR + '/MaturityIndicators/Gen2', RES_DIR)
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

def readRDF(filename):
    """
    Open and parse RDF document.
    """

    g = rdflib.ConjunctiveGraph()
    result = g.parse(filename, format='trig')


    # for subj, pred, obj in g:
    #     print(subj, pred, obj)
    #     if (subj, pred, obj) not in g:
    #         raise Exception("It better be!")

    # print(len(result))
    rdf_string = g.serialize(format="trig").decode("utf-8")
    # print(rdf_string)

    # print(s)
    # for s, p, o in g.triples( (None, RDF.type, None) ):
    #     # print(p)
    #     print("%s is a %s"%(s,o))


    return g, rdf_string

def getPrefix(string):
    # print(string)
    prog = re.compile(RE_PATTERN_PREFIX)
    result_list = prog.findall(string)
    prefix = ''
    for result in result_list:
        prefix += "PREFIX " + result[0] + " " + result[1] + "\n"

    return prefix

def makeGraph(rdf_object):
    """
    Make a graph wich is the visual representaton of the RDF object.
    """

    G = rdflib_to_networkx_multidigraph(rdf_object)

    # Plot Networkx instance of RDF Graph
    pos = nx.spring_layout(G, scale=2)
    edge_labels = nx.get_edge_attributes(G, 'r')
    nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
    nx.draw(G, with_labels=True)
    plt.savefig("test")



def requestOnRDF(rdf_object, term, prefix):
    """
    Make a request on an rdflib object.
    """

    # queryString = """
    #         PREFIX dc:<http://purl.org/dc/terms/>
    #         SELECT ?x ?name
    #         WHERE { ?x dc:publisher ?name } limit 50
    #         """
    #
    # sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    # sparql.addDefaultGraph("http://www.example.org/graph-selected")

    # term = "fairmi:measuring"

    s = Template(
        """
        $prefix
        SELECT ?s ?p ?o
        WHERE { ?s $term ?o } limit 50
        """)

    query_string = s.substitute(prefix=prefix, term=term)


    query_res = rdf_object.query(query_string)
    color = "cyan"
    if term == "rdfs:label": color = "yellow"
    print(term.replace(term, termcolor.colored(term, color) + ": "), end="")
    for s, p, o in query_res:
        # print("%s publisher %s" % row)
        print(o)

    return query_res


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

def sortFAIRList(list):
    list.sort()

if __name__ == "__main__":
    if not os.path.isdir(TEMP_DIR):
        cloneRepo()

    if os.path.isdir(RES_DIR):
        removeDir(RES_DIR)

    getGen2MaturityIndicators()

    if os.path.isdir(TEMP_DIR):
        removeDir(TEMP_DIR)

    list_res_files = listDirFiles(RES_DIR)

    terms_list = ["fairmi:measuring", "fairmi:procedure", "fairmi:validation"]

    for filename in list_res_files:
        try:
            graph, rdf_string = readRDF(RES_DIR + '/' + filename)
            prefix = getPrefix(rdf_string)
            print("\n###########################", end="\n\n")
            print(filename.replace(filename, termcolor.colored(filename, "yellow")))
            for term in terms_list:
                query_res = requestOnRDF(graph, term, prefix)
                # makeGraph(query_res)
        except rdflib.plugins.parsers.notation3.BadSyntax:
            pass
