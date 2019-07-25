#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import joblib
from joblib import Parallel, delayed
import multiprocessing
from multiprocessing import Pool, freeze_support, RLock, Lock, Array, Manager
from tqdm import tqdm
from tqdm import trange

from reprint import output
import time
import random

import test_metric
import multi_progress
# from test_metric import getMetrics
# from module_metrics.testMetrics import testMetrics

PRINT_DETAILS = False
FILENAME = ""
OUTPUT_DIR = "output"

# GLOBAL_PBAR = tqdm()

# class Pbar:
#     def __init__(self, global_pbar):
#         self.global_pbar = global_pbar
#     def getPbar():
#         return self.global_pbar


def readDOIsFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

def multiTestMetrics(tuple_GUID):
    # COUNT=0
    # COUNT += 1
    # dois_num = COUNT

    count = int(tuple_GUID[0] + 1)
    position_holders = tuple_GUID[1][4]
    position = multi_progress.get_position(position_holders)
    total = tuple_GUID[1][3]
    metrics_info = tuple_GUID[1][2]10 * offset, offset
    text = tuple_GUID[1][1]
    GUID = tuple_GUID[1][0]


    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    # metrics = test_metric.getMetrics()

    test_line_list = [GUID]
    headers_list = ["GUID"]

    # print(count)

    pbar = tqdm(total=len(metrics_info), position=position, desc=GUID, dynamic_ncols=True, unit='MI_test', ascii=' #', leave=False)

    for metric_info in metrics_info:
        time.sleep(0.05)
        pbar.update(1)



        # metric_info = test_metric.processFunction(test_metric.getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
        # metric_info = getMetricInfo(metric["@id"])
        principle = metric_info["principle"].rsplit('/', 1)[-1]

        pbar.set_description('[' + str(count) + '/' + str(total) + ']' + ' Test [' + principle + '] for [' + GUID + ']')

        if principle[0] == 'I':
            if PRINT_DETAILS:
                # print informations related to the metric
                printMetricInfo(metric_info)

            # evaluate the metric
            metric_evaluation_result = test_metric.processFunction(test_metric.testMetric, [metric_info["smarturl"], data], 'Evaluating metric... ')

            if PRINT_DETAILS:
                #print results of the evaluation
                printTestMetricComment('http://schema.org/comment', metric_evaluation_result)
                printTestMetricScore('http://semanticscience.org/resource/SIO_000300', metric_evaluation_result)

            # get the score
            score = metric_evaluation_result[0]['http://semanticscience.org/resource/SIO_000300'][0]['@value']
            score = str(int(float(score)))

            test_line_list.append(score)
            headers_list.append(principle)

        # GLOBAL_PBAR.refresh()

    time.sleep(0.5)
    multi_progress.release_position(position_holders, position)


    dirpath = os.path.dirname(os.getcwd() + "/" + os.path.basename(FILENAME.split("-")[0]))
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    output = OUTPUT_DIR + "/" + os.path.basename(FILENAME).replace(".txt", ".tsv")
    test_metric.writeLineToFile("\t".join(test_line_list), "\t".join(headers_list), dirpath + "/" + output)

if __name__ == "__main__":
    # print("start the output")
    #
    # with output(initial_len=3, interval=0) as output_lines:
    #     while True:
    #         output_lines[0] = "First_line  {}...".format(random.randint(1,10))
    #         output_lines[1] = "Second_line {}...".format(random.randint(1,10))
    #         output_lines[2] = "Third_line  {}...".format(random.randint(1,10))
    #         time.sleep(0.5)

    FILENAME = sys.argv[1]
    data = readDOIsFile(FILENAME)

    dois_list = data.split("\n")

    num_cores = multiprocessing.cpu_count()
    # num_cores = 12
    # executing metrics evaluations
    # setting up multi process/progressbars
    maxrows = num_cores + 1
    m = Manager()
    p = Pool(num_cores, initializer=multi_progress.init, initargs=(RLock(), m.Lock()))
    position_holders = m.Array('i', [0] * maxrows)


    list_results = []

    metrics_info = []
    metrics = test_metric.getMetrics()
    metrics_pbar = tqdm(metrics, total=len(metrics), position=1)
    for metric in metrics:
        principle = metric["principle"].rsplit('/', 1)[-1]

        metrics_pbar.update(1)
        metrics_pbar.set_description('Retrieving [' + principle + '] metric informations...')
        metrics_info.append(test_metric.processFunction(test_metric.getMetricInfo, [metric["@id"]], 'Retrieving metric informations... '))

    metrics_pbar.set_description('Retrieving metrics informations [DONE]')
    print("\n")




    new_dois_list = []
    with output(initial_len=len(dois_list), interval=0) as output_lines:
        for i, doi in enumerate(dois_list):
            new_dois_list.append((doi, output_lines[i], metrics_info, len(dois_list), position_holders))

    GLOBAL_PBAR = tqdm(total=len(dois_list), desc="Total", unit="DOI", position=maxrows+1, leave=True)


    for i, result in enumerate(p.imap(multiTestMetrics, enumerate(new_dois_list), chunksize=1)):
        # pbar = tqdm(total=len(dois_list), position=0, desc="Total", initial=i+1, unit="DOI")
        time.sleep(0.1)
        GLOBAL_PBAR.update(1)
        GLOBAL_PBAR.refresh()
        list_results.append(result)


    # [x.wait() for x in res]
    # # Other threads output isn't tracked by this thread, so add newlines to move below the progress bars.
    #
    print("\n" * maxrows)

    p.close()
    p.join()

    # for doi in data.split("\n"):
    #     TM.testMetrics(doi)
