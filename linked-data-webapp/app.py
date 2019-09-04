import csv
from flask import Flask, redirect, url_for, request, render_template
import random

from rdflib import ConjunctiveGraph

app = Flask(__name__)

ns = {"nb": "http://bise-eu.info/core-ontology#",
      "dc": "http://dcterms/",
      "p-plan": "http://purl.org/net/p-plan#",
      "edam": "http://purl.obolibrary.org/obo/edam#"}

g = ConjunctiveGraph()
g.parse("static/data/neubias-latest.ttl", format="turtle")
g.parse("static/data/EDAM-bioimaging_alpha03.owl")
print(str(len(g)) + ' triples in Biii data graph')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/curation_needs_demo')
def curation_needs_demo():

    # NO PUBLICATION
    q_no_publication = """
    SELECT (count(?title) as ?nb_soft) WHERE {
        ?s rdf:type <http://biii.eu/node/software> .
        ?s dc:title ?title .
        FILTER NOT EXISTS {?s nb:hasReferencePublication ?publication} .
    }
    """
    q_no_publication_entries = """
    SELECT ?s ?title WHERE {
        ?s rdf:type <http://biii.eu/node/software> .
        ?s dc:title ?title .
        FILTER NOT EXISTS {?s nb:hasReferencePublication ?publication} .
    }
    """
    results = g.query(q_no_publication, initNs=ns)
    count_no_pub = 0
    for r in results:
        print(r)
        count_no_pub = str(r["nb_soft"])

    results = g.query(q_no_publication_entries, initNs=ns)
    no_pub = []
    for r in results:
        no_pub.append({"title": r["title"], "url": r["s"]})
    if len(no_pub) > 5:
        no_pub = random.sample(no_pub, 10)

    # NO EDAM TOPIC OR FUNCTION
    q_no_edam = """
        SELECT (count(?title) as ?nb_soft) WHERE {
            ?s rdf:type <http://biii.eu/node/software> .
            ?s dc:title ?title .
            FILTER NOT EXISTS {?s nb:hasTopic ?topic} .
            FILTER NOT EXISTS {?s nb:hasFunction ?operation} .
        }
        """
    results = g.query(q_no_edam, initNs=ns)
    count_no_edam = 0
    for r in results:
        count_no_edam = str(r["nb_soft"])

    q_no_edam_entries = """
        SELECT ?s ?title WHERE {
            ?s rdf:type <http://biii.eu/node/software> .
            ?s dc:title ?title .
            FILTER NOT EXISTS {?s nb:hasTopic ?topic} .
            FILTER NOT EXISTS {?s nb:hasFunction ?operation} .
        }
        """
    results = g.query(q_no_edam_entries, initNs=ns)
    no_edam = []
    for r in results:
        no_edam.append({"title": r["title"], "url": r["s"]})
    if len(no_edam) > 5:
        no_edam = random.sample(no_edam, 10)

    return render_template('demo_curation_needs.html',
                           count_no_pub=count_no_pub,
                           count_no_edam=count_no_edam,
                           missing_publication = no_pub,
                           missing_edam=no_edam)


@app.route('/comulis_demo')
def comulis_demo():
    q_segmentation = """
    SELECT DISTINCT ?soft ?title 
        (group_concat(?function_label;separator="|") as ?operations)
        (group_concat(?topic_label;separator="|") as ?topics) 
        WHERE { 
        ?soft a <http://biii.eu/node/software> .
        ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function .
        ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_segmentation> . 
        ?edam_function rdfs:label ?function_label .
        ?soft dc:title ?title .
        
        OPTIONAL {
            ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
            ?edam_topic rdfs:label ?topic_label .
        }
    }
    GROUP BY ?soft
    ORDER BY ?title
    """

    q_registration = """
    SELECT DISTINCT ?soft ?title 
        (group_concat(?function_label;separator="|") as ?operations)
        (group_concat(?topic_label;separator="|") as ?topics) 
    WHERE { 
        ?soft a <http://biii.eu/node/software> .
        ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function . 
        ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_registration> . 
        ?edam_function rdfs:label ?function_label . 
        ?soft dc:title ?title .
        
        OPTIONAL {
            ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
            ?edam_topic rdfs:label ?topic_label .
        }
    }
    GROUP BY ?soft
    ORDER BY ?title
    """

    q_visualisation = """
    SELECT DISTINCT ?soft ?title 
        (group_concat(?function_label;separator="|") as ?operations)
        (group_concat(?topic_label;separator="|") as ?topics)
    WHERE { 
        ?soft a <http://biii.eu/node/software> .
        ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function .
        ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_visualisation> . 
        ?edam_function rdfs:label ?function_label .

        ?soft dc:title ?title .
        
        OPTIONAL {
            ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
            ?edam_topic rdfs:label ?topic_label .
        }
    }
    GROUP BY ?soft
    ORDER BY ?title
    """

    seg_entries = []
    results = g.query(q_segmentation, initNs=ns)
    for r in results:
        title = str(r["title"])
        url = str(r["soft"])
        operations = list(set(str(r["operations"]).split("|")))
        operations = filter(None, operations)
        topics = list(set(str(r["topics"]).split("|")))
        topics = filter(None, topics)
        seg_entries.append({"title":title, "url":url, "operations":operations, "topics":topics})

    reg_entries = []
    results = g.query(q_registration, initNs=ns)
    for r in results:
        title = str(r["title"])
        url = str(r["soft"])
        operations = list(set(str(r["operations"]).split("|")))
        operations = filter(None, operations)
        topics = list(set(str(r["topics"]).split("|")))
        topics = filter(None, topics)
        reg_entries.append({"title": title, "url": url, "operations": operations, "topics": topics})

    vis_entries = []
    results = g.query(q_visualisation, initNs=ns)
    for r in results:
        title = str(r["title"])
        url = str(r["soft"])
        operations = list(set(str(r["operations"]).split("|")))
        operations = filter(None, operations)
        topics = list(set(str(r["topics"]).split("|")))
        topics = filter(None, topics)
        vis_entries.append({"title": title, "url": url, "operations": operations, "topics": topics})

    return render_template('demo_comulis.html', seg_entries=seg_entries, reg_entries=reg_entries, vis_entries=vis_entries)



if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)