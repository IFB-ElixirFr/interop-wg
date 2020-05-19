import csv
from flask import Flask, redirect, url_for, request, render_template
from flask_socketio import SocketIO
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import threading

import time
import random

from rdflib import ConjunctiveGraph

import sys
sys.path.append('../fairmetrics_interface_tests')

import test_metric

# Command line exec
import subprocess
from subprocess import Popen
from subprocess import PIPE
from subprocess import run

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('hello')
def handle_hello(json):
    print('received hello from client: ' + str(json))
    multiple_tasks()

@socketio.on('hello')
def emit_hi(json):
    print('sending hi from server')
    socketio.emit('hi response', json, broadcast=True)
    print('sent')

def long_task(iteration, size):
    time.sleep(5)
    print("long task done")
    return ('long', iteration/size*100)

def short_task(iteration, size):
    time.sleep(1)
    print("short task done")
    return ('short', iteration/size*100)

@socketio.on('start_process')
def multiple_tasks():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        tasks = []
        long_size = 10
        for i in range(0,long_size):
            future = executor.submit(long_task, i+1, long_size)
            tasks.append(future)


        short_size = 40
        for i in range(0,short_size):
            future = executor.submit(short_task, i+1, short_size)
            tasks.append(future)


        for future in concurrent.futures.as_completed(tasks):
            try:
                type, value = future.result()
                if type == 'short':
                    socketio.emit('p1.value', value, broadcast=True)
                elif type == 'long':
                    socketio.emit('p2.value', value, broadcast=True)
            except Exception as exc:
                print('generated an exception: %s' % (exc))
            else:
                print('DONE for all tasks')




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_asynch')
def test_asynch():
    progress = {}
    progress['a'] = 0
    progress['b'] = 0
    print("CALL to test_asynch")

    emit_hi({'data': 'hi message from server'})
    socketio.emit('my ack', progress, broadcast=True)
    socketio.emit('p1.value', progress, broadcast=True)
    socketio.emit('p2.value', progress, broadcast=True)


    #multiple_tasks()
    return render_template('test_asynch.html', progress=progress)

@app.route('/is_it_fair')
def is_it_fair():
    return render_template('is_it_fair.html', )

@app.route('/test_url', methods=['POST'])
def testUrl():
    test_url = request.form.get('url')

    number = test_metric.getMetrics()
    # socketio.emit('newnumber', {'number': number}, namespace='/test')
    socketio.emit('my response', {'data': 'got it!'}, namespace='/test')

    headers_list, descriptions_list, test_score_list, time_list, comments_list = test_metric.webTestMetrics(test_url)

    results_list = []
    for i, elem in enumerate(headers_list):
        if i != 0:
            res_dict = {}
            res_dict["header"] = headers_list[i]
            res_dict["score"] = test_score_list[i]
            res_dict["time"] = time_list[i]
            try:
                res_dict["comments"] = comments_list[i].replace('\n', '<br>')
                res_dict["descriptions"] = descriptions_list[i]
            except IndexError:
                res_dict["comments"] = ""
                res_dict["descriptions"] = ""
            results_list.append(res_dict)
        if i == 4:
            print(res_dict)

    return render_template('result.html', test_url=test_url,
                                            results_list=results_list,)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
    socketio.run(app, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)


























# ns = {"nb": "http://bise-eu.info/core-ontology#",
#       "dc": "http://dcterms/",
#       "p-plan": "http://purl.org/net/p-plan#",
#       "edam": "http://purl.obolibrary.org/obo/edam#"}
#
# g = ConjunctiveGraph()
# g.parse("static/data/neubias-latest.ttl", format="turtle")
# g.parse("static/data/EDAM-bioimaging_alpha03.owl")
# print(str(len(g)) + ' triples in Biii data graph')
#
#
# @app.route('/curation_needs_demo')
# def curation_needs_demo():
#
#     # NO PUBLICATION
#     q_no_publication = """
#     SELECT (count(?title) as ?nb_soft) WHERE {
#         ?s rdf:type <http://biii.eu/node/software> .
#         ?s dc:title ?title .
#         FILTER NOT EXISTS {?s nb:hasReferencePublication ?publication} .
#     }
#     """
#     q_no_publication_entries = """
#     SELECT ?s ?title WHERE {
#         ?s rdf:type <http://biii.eu/node/software> .
#         ?s dc:title ?title .
#         FILTER NOT EXISTS {?s nb:hasReferencePublication ?publication} .
#     }
#     """
#     results = g.query(q_no_publication, initNs=ns)
#     count_no_pub = 0
#     for r in results:
#         print(r)
#         count_no_pub = str(r["nb_soft"])
#
#     results = g.query(q_no_publication_entries, initNs=ns)
#     no_pub = []
#     for r in results:
#         no_pub.append({"title": r["title"], "url": r["s"]})
#     if len(no_pub) > 5:
#         no_pub = random.sample(no_pub, 10)
#
#     # NO EDAM TOPIC OR FUNCTION
#     q_no_edam = """
#         SELECT (count(?title) as ?nb_soft) WHERE {
#             ?s rdf:type <http://biii.eu/node/software> .
#             ?s dc:title ?title .
#             FILTER NOT EXISTS {?s nb:hasTopic ?topic} .
#             FILTER NOT EXISTS {?s nb:hasFunction ?operation} .
#         }
#         """
#     results = g.query(q_no_edam, initNs=ns)
#     count_no_edam = 0
#     for r in results:
#         count_no_edam = str(r["nb_soft"])
#
#     q_no_edam_entries = """
#         SELECT ?s ?title WHERE {
#             ?s rdf:type <http://biii.eu/node/software> .
#             ?s dc:title ?title .
#             FILTER NOT EXISTS {?s nb:hasTopic ?topic} .
#             FILTER NOT EXISTS {?s nb:hasFunction ?operation} .
#         }
#         """
#     results = g.query(q_no_edam_entries, initNs=ns)
#     no_edam = []
#     for r in results:
#         no_edam.append({"title": r["title"], "url": r["s"]})
#     if len(no_edam) > 5:
#         no_edam = random.sample(no_edam, 10)
#
#     return render_template('demo_curation_needs.html',
#                            count_no_pub=count_no_pub,
#                            count_no_edam=count_no_edam,
#                            missing_publication = no_pub,
#                            missing_edam=no_edam)
#
#
# @app.route('/comulis_demo')
# def comulis_demo():
#     q_segmentation = """
#     SELECT DISTINCT ?soft ?title
#         (group_concat(?function_label;separator="|") as ?operations)
#         (group_concat(?topic_label;separator="|") as ?topics)
#         WHERE {
#         ?soft a <http://biii.eu/node/software> .
#         ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function .
#         ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_segmentation> .
#         ?edam_function rdfs:label ?function_label .
#         ?soft dc:title ?title .
#
#         OPTIONAL {
#             ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
#             ?edam_topic rdfs:label ?topic_label .
#         }
#     }
#     GROUP BY ?soft
#     ORDER BY ?title
#     """
#
#     q_registration = """
#     SELECT DISTINCT ?soft ?title
#         (group_concat(?function_label;separator="|") as ?operations)
#         (group_concat(?topic_label;separator="|") as ?topics)
#     WHERE {
#         ?soft a <http://biii.eu/node/software> .
#         ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function .
#         ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_registration> .
#         ?edam_function rdfs:label ?function_label .
#         ?soft dc:title ?title .
#
#         OPTIONAL {
#             ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
#             ?edam_topic rdfs:label ?topic_label .
#         }
#     }
#     GROUP BY ?soft
#     ORDER BY ?title
#     """
#
#     q_visualisation = """
#     SELECT DISTINCT ?soft ?title
#         (group_concat(?function_label;separator="|") as ?operations)
#         (group_concat(?topic_label;separator="|") as ?topics)
#     WHERE {
#         ?soft a <http://biii.eu/node/software> .
#         ?soft <http://bise-eu.info/core-ontology#hasFunction> ?edam_function .
#         ?edam_function rdfs:subClassOf* <http://edamontology.org/operation_Image_visualisation> .
#         ?edam_function rdfs:label ?function_label .
#
#         ?soft dc:title ?title .
#
#         OPTIONAL {
#             ?soft <http://bise-eu.info/core-ontology#hasTopic> ?edam_topic .
#             ?edam_topic rdfs:label ?topic_label .
#         }
#     }
#     GROUP BY ?soft
#     ORDER BY ?title
#     """
#
#     seg_entries = []
#     results = g.query(q_segmentation, initNs=ns)
#     for r in results:
#         title = str(r["title"])
#         url = str(r["soft"])
#         operations = list(set(str(r["operations"]).split("|")))
#         operations = filter(None, operations)
#         topics = list(set(str(r["topics"]).split("|")))
#         topics = filter(None, topics)
#         seg_entries.append({"title":title, "url":url, "operations":operations, "topics":topics})
#
#     reg_entries = []
#     results = g.query(q_registration, initNs=ns)
#     for r in results:
#         title = str(r["title"])
#         url = str(r["soft"])
#         operations = list(set(str(r["operations"]).split("|")))
#         operations = filter(None, operations)
#         topics = list(set(str(r["topics"]).split("|")))
#         topics = filter(None, topics)
#         reg_entries.append({"title": title, "url": url, "operations": operations, "topics": topics})
#
#     vis_entries = []
#     results = g.query(q_visualisation, initNs=ns)
#     for r in results:
#         title = str(r["title"])
#         url = str(r["soft"])
#         operations = list(set(str(r["operations"]).split("|")))
#         operations = filter(None, operations)
#         topics = list(set(str(r["topics"]).split("|")))
#         topics = filter(None, topics)
#         vis_entries.append({"title": title, "url": url, "operations": operations, "topics": topics})
#
#     return render_template('demo_comulis.html', seg_entries=seg_entries, reg_entries=reg_entries, vis_entries=vis_entries)
