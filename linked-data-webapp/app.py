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
#socketio = SocketIO(app,async_mode = 'eventlet')
socketio = SocketIO(app)

connections = []

@socketio.on('connected')
def handle_connected(json):
    print(request.namespace.socket.sessid)
    print(request.namespace)

@socketio.on('hello')
def handle_hello(json):
    print(request.sid)
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
                    socketio.emit('p1.value', value)
                elif type == 'long':
                    socketio.emit('p2.value', value)
            except Exception as exc:
                print('generated an exception: %s' % (exc))
            else:
                print('DONE for all tasks')



    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    # emit('ack', 'everything is fine')
#
# @socketio.on('slow')
# def handle_slow():
#     print('received slow from client: ' + str(request.sid))
#     #socketio.emit('ack', 'everything is fine', broadcast=True)
#     #emit('ack', 'everything is fine', broadcast=True)
#     for i in range(0,100):
#         time.sleep(0.5)
#         emit('slow', i)
#         i+=10
#     emit('slow', 'done')
#
# @socketio.on('fast')
# def handle_fast():
#     print('received slow fast client: ' + str(request.sid))
#     #socketio.emit('ack', 'everything is fine', broadcast=True)
#     #emit('ack', 'everything is fine', broadcast=True)
#     for i in range(0,100):
#         time.sleep(0.2)
#         emit('fast', i)
#         i+=2
#     emit('fast', 'done')
#
# @socketio.on('long')
# def handle_long():
#     print("long task for " + request.sid)
#     long_task()
#     emit('long', 'long task done')
#
# def long_task():
#     print('long long long)')
#     time.sleep(5)



@app.route('/')
def index():
    return render_template('index.html')

def cb():
    print("received message originating from server")

@app.route('/test_asynch')
def test_asynch():
    return render_template('test_asynch.html')

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
