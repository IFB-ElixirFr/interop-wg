#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
from string import Template


from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/search/<term>")
def requestRes(term):
    """
    Display a web page with the request result
    """
    rdf_object = readRDF()
    select_result = requestOnRDF(rdf_object, term)
    display = "Term test: " + term + "<br>"

    # each line of the result
    for row in select_result:
        display = display + str(row) + "<br>"

    return display

def readRDF():
    """
    Open and parse RDF document.
    """

    g = rdflib.Graph()
    result = g.parse("./biotoolsRdf/biotools-dump-20171129.ttl", format='turtle')
    # result = g.parse("http://www.w3.org/People/Berners-Lee/card")

    print("graph has %s statements." % len(g))
    # prints graph has 79 statements.

    # for subj, pred, obj in g:
    #     if (subj, pred, obj) not in g:
    #         raise Exception("It better be!")


    # s = g.serialize(format='n3')
    return result



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

def requestOnRDF(rdf_object, term):
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

    query_res = rdf_object.query("""
                    PREFIX dc:<http://purl.org/dc/terms/>
                    SELECT *
                    WHERE { ?s ?p search } limit 50
                    """, initsNs={ 'search': term})

    for row in query_res:
        # print("%s publisher %s" % row)
        print(row)

    return(query_res)



if __name__ == "__main__":
    rdf_object = readRDF()
    select_result = requestOnRDF(rdf_object)
    makeGraph(select_result)
    requestRes(select_result)
