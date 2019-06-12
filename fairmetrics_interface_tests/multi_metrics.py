#!/usr/bin/python3
# -*- coding: utf-8 -*-

import joblib
from joblib import Parallel, delayed
import multiprocessing
from multiprocessing import Pool
import tqdm

from reprint import output
import time
import random

import test_metric
# from test_metric import getMetrics
# from module_metrics.testMetrics import testMetrics

PRINT_DETAILS = False

def readDOIsFile(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

COUNT = 0

def multiTestMetrics(GUID):
    # COUNT=0
    # COUNT += 1
    # dois_num = COUNT

    count = int(GUID[0] + 1)
    total = GUID[1][3]
    metrics_info = GUID[1][2]
    text = GUID[1][1]
    GUID = GUID[1][0]

    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    # metrics = test_metric.getMetrics()

    test_line_list = [GUID]
    headers_list = ["GUID"]

    # print(count)
    n = 0
    pbar = tqdm.tqdm(total=len(metrics_info), position=count + 1, desc=GUID, dynamic_ncols=True, unit='MIs_test', ascii=' #', miniters=1)

    for metric_info in metrics_info:
        time.sleep(0.5)
        pbar.update(1)
        n += 1


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

    test_metric.writeLineToFile("\t".join(test_line_list), "\t".join(headers_list))

if __name__ == "__main__":

    # print("start the output")
    #
    # with output(initial_len=3, interval=0) as output_lines:
    #     while True:
    #         output_lines[0] = "First_line  {}...".format(random.randint(1,10))
    #         output_lines[1] = "Second_line {}...".format(random.randint(1,10))
    #         output_lines[2] = "Third_line  {}...".format(random.randint(1,10))
    #         time.sleep(0.5)

    data = readDOIsFile('./bioinformatic_DOIs.txt')

    dois_list = data.split("\n")

    num_cores = multiprocessing.cpu_count()

    # executing metrics evaluations
    p = Pool(num_cores)
    list_results = []

    metrics_info = []
    metrics = test_metric.getMetrics()
    metrics_pbar = tqdm.tqdm(metrics, total=len(metrics), position=0)
    for metric in metrics:
        principle = metric["principle"].rsplit('/', 1)[-1]

        metrics_pbar.update(1)
        metrics_pbar.set_description('Retrieving [' + principle + '] metric informations...')
        metrics_info.append(test_metric.processFunction(test_metric.getMetricInfo, [metric["@id"]], 'Retrieving metric informations... '))

    new_dois_list = []
    with output(initial_len=6489, interval=0) as output_lines:
        for i, doi in enumerate(dois_list):
            new_dois_list.append((doi, output_lines[i], metrics_info, len(dois_list)))

    pbar = tqdm.tqdm(total=len(dois_list), position=num_cores+3, desc="Total", unit="DOI", maxinterval=1, miniters=0)
    for i, result in enumerate(p.imap(multiTestMetrics, enumerate(new_dois_list), chunksize=1)):
        pbar = tqdm.tqdm(total=len(dois_list), position=num_cores+i+3, desc="Total", initial=i+1, unit="DOI", maxinterval=1, miniters=0)

        list_results.append(result)



    p.close()
    p.join()

    # for doi in data.split("\n"):
    #     TM.testMetrics(doi)
