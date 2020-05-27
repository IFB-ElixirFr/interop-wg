import eventlet
eventlet.monkey_patch()

from flask import Flask, redirect, url_for, request, render_template, session
from flask_socketio import SocketIO
from flask_socketio import send, emit
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import threading

import time
import random
import re

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
#socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app,async_mode = 'eventlet')
#socketio = SocketIO(app)

metrics = [{'name':'f1', 'category':'F', 'description': 'F1 verifies that ...  '},
           {'name':'f2', 'category':'F', 'description': 'F2 verifies that ...  '},
           {'name':'f3', 'category':'F', 'description': 'F3 verifies that ...  '},
           {'name':'a1', 'category':'A'},
           {'name':'a2', 'category':'A'}]


@socketio.on('evaluate_metric')
def handle_metric(json):
    url = json['url']
    api_url = json['api_url']
    id = json['id']
    principle = json['principle']
    print('RUNNING ' + principle + ' for '+str(url))
    emit('running_f')
    data = '{"subject": "' + url + '"}'
    print(data)


    # evaluate metric
    start_time = test_metric.getCurrentTime()
    res = test_metric.testMetric(api_url, data)
    print(res)
    end_time = test_metric.getCurrentTime()
    evaluation_time = end_time - start_time
    print(evaluation_time)

    # get the score
    score = test_metric.requestResultSparql(res, "ss:SIO_000300")
    score = str(int(float(score)))

    # get comment
    comment = test_metric.requestResultSparql(res, "schema:comment")
    # remove empty lines from the comment
    comment = test_metric.cleanComment(comment)
    # select only success and failure
    comment = test_metric.filterComment(comment, "sf")

    emit('done_' + id, {"score": score, "comment": comment, "time": str(evaluation_time)})
    print('DONE ' + principle)

@socketio.on('connected')
def handle_connected(json):
    print(request.namespace.socket.sessid)
    print(request.namespace)

@socketio.on('hello')
def handle_hello(json):
    print(request.sid)
    print('received hello from client: ' + str(json))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    emit('ack', 'everything is fine')

@socketio.on('slow')
def handle_slow():
    print('received slow from client: ' + str(request.sid))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    for i in range(0,100):
        time.sleep(0.5)
        emit('slow', i)
        i+=10
    emit('slow', 'done')

@socketio.on('fast')
def handle_fast():
    print('received fast client: ' + str(request.sid))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    for i in range(0,100):
        time.sleep(0.01)
        emit('fast', i)
    emit('fast', 'done')

@socketio.on('long')
def handle_long():
    print("long task for " + request.sid)
    long_task()
    emit('long', 'long task done')

def long_task():
    print('long long long)')
    time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

def cb():
    print("received message originating from server")

@app.route('/test_asynch')
def test_asynch():
    #return render_template('test_asynch.html')
    metrics = []
    ###### A DEPLACER AU LANCEMENT DU SERVEUR ######
    metrics_res = test_metric.getMetrics()
    for metric in metrics_res:
        # remove "FAIR Metrics Gen2" from metric name
        name = metric["name"].replace('FAIR Metrics Gen2- ','')
        # same but other syntax because of typo
        name = name.replace('FAIR Metrics Gen2 - ','')
        metrics.append({
            "name": name,
            "description": metric["description"],
            "api_url": metric["smarturl"],
            "id": "metric_" + metric["@id"].rsplit('/', 1)[-1],
            "principle": metric["principle"],
            "principle_tag": metric["principle"].rsplit('/', 1)[-1],
            "principle_category": metric["principle"].rsplit('/', 1)[-1][0],
        })

    return render_template('metrics_summary.html', f_metrics=metrics)

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
    socketio.run(app,  host="0.0.0.0", port=5000, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)
