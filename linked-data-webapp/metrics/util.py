from SPARQLWrapper import SPARQLWrapper, N3, JSON, RDF, TURTLE, JSONLD
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
import requests

import re

# DOI regex
regex = r"10.\d{4,9}\/[-._;()\/:A-Z0-9]+"

# Describe datacite
def describe_opencitation(uri, g):
    # g = Graph()
    print(f'SPARQL for [ {uri} ] with enpoint [ Opencitation ]')
    sparql = SPARQLWrapper("https://opencitations.net/sparql")
    sparql.setQuery("""
            PREFIX cito: <http://purl.org/spar/cito/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX datacite: <http://purl.org/spar/datacite/>
            PREFIX literal: <http://www.essepuntato.it/2010/06/literalreification/>
            PREFIX biro: <http://purl.org/spar/biro/>
            PREFIX frbr: <http://purl.org/vocab/frbr/core#>
            PREFIX c4o: <http://purl.org/spar/c4o/>

            DESCRIBE ?x WHERE {
                ?x datacite:hasIdentifier/literal:hasLiteralValue '""" + uri + """' 
            }
    """)

    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()
    print("Results: " + str(len(results)))

    results = results.serialize(format='turtle').decode()

    g.parse(data=results, format="turtle")

    # print(g.serialize(format='turtle').decode())
    return g

# Describe lod.openaire
def describe_loa(uri, g):
    # g = Graph()
    print(f'SPARQL for [ {uri} ] with enpoint [ LOA ]')
    sparql = SPARQLWrapper("http://lod.openaire.eu/sparql")
    sparql.setQuery("""
            DESCRIBE ?x WHERE {   
            ?x <http://lod.openaire.eu/vocab/resPersistentID> '""" + uri + """' 
            }
    """)

    g_len = Graph()
    sparql.setReturnFormat(N3)
    results = sparql.query().convert()
    print("Results: " + str(len(g_len.parse(data=results, format="n3"))))
    g.parse(data=results, format="n3")

    # print(g.serialize(format='turtle').decode())
    return g


# Describe Wikidata
def describe_wikidata(uri, g):
    # g = Graph()
    print(f'SPARQL for [ {uri} ] with enpoint [ Wikidata ]')
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX p: <http://www.wikidata.org/prop/>
            PREFIX ps: <http://www.wikidata.org/prop/statement/>
            PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX bd: <http://www.bigdata.com/rdf#>

            DESCRIBE ?x WHERE {   
                ?x wdt:P356 '""" + uri + """' 
            }
    """)

    sparql.setReturnFormat(N3)
    results = sparql.query().convert()
    print("Results: " + str(len(results)))
    results = results.serialize(format='turtle').decode()

    g.parse(data=results, format="n3")

    # print(g.serialize(format='turtle').decode())
    return g

# Describe a tool based on experimental bio.tools SPARQL endpoint
def describe_biotools(uri, g):
    print(f'SPARQL for [ {uri} ] with enpoint [ bio.tools ]')

    h = {'Accept': 'text/turtle'}
    p = {'query': "DESCRIBE <" + uri + ">"}
    res = requests.get("https://134.158.247.76/sparql", headers=h, params=p, verify=False)

    g.parse(data=res.text, format="turtle")

    #print(g.serialize(format='turtle').decode())
    return g


def is_DOI(uri):
    return bool(re.search(regex, uri, re.MULTILINE | re.IGNORECASE))

def get_DOI(uri):
    match = re.search(regex, uri, re.MULTILINE | re.IGNORECASE)
    return match.group(0)

def ask_OLS(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in OLS.
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in OLS, False otherwise.
    """
    print(f'call to the OLS REST API for [ {uri} ]')
    h = {'Accept': 'application/json'}
    p = {'iri': uri}
    res = requests.get("http://www.ebi.ac.uk/ols/api/terms", headers=h, params=p, verify=False)

    if res.json()['page']['totalElements'] > 0:
        return True
    else:
        return False

def ask_LOV(uri):
    """
    Checks that the URI is registered in one of the ontologies indexed in LOV (Linked Open Vocabularies).
    :param uri:
    :return: True if the URI is registered in one of the ontologies indexed in LOV, False otherwise.
    """
    print(f'SPARQL for [ {uri} ] with enpoint [ https://lov.linkeddata.es/dataset/lov/sparql ]')

    h = {'Accept': 'application/sparql-results+json'}
    p = {'query': "ASK { ?s ?p <" + uri + ">}"}
    res = requests.get("https://lov.linkeddata.es/dataset/lov/sparql", headers=h, params=p, verify=False)

    #print(res.text)
    return res.json()['boolean']

# def ask_BioPortal(uri):
#     """
#
#     http://sparql.bioontology.org
#
#     Checks that the URI is registered in one of the ontologies indexed in OLS.
#     :param uri:
#     :return: True if the URI is registered in one of the ontologies indexed in OLS, False otherwise.
#     """
#     print(f'SPARQL for [ {uri} ] with enpoint [ http://sparql.bioontology.org ]')
#
#     h = {'Accept': 'application/sparql-results+json'}
#     p = {'query': "ASK { ?s ?p <" + uri + ">}"}
#     res = requests.get("http://sparql.bioontology.org/sparql", headers=h, params=p, verify=False)
#
#     print(res.text)
#     return res.json()['boolean']