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
OUTPUT_DIR = "output_6"
NUMBER_DOIS = 6

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
    """
    Call multiples time "testMetric" to test each metric against one GUID.

    @param GUID Tuplue The GUID to be tested plus other related informations
    """
    # COUNT=0
    # COUNT += 1
    # dois_num = COUNT

    count = int(tuple_GUID[0] + 1)
    position_holders = tuple_GUID[1][4]
    position = multi_progress.get_position(position_holders)
    total = tuple_GUID[1][3]
    metrics_info = tuple_GUID[1][2]
    text = tuple_GUID[1][1]
    GUID = tuple_GUID[1][0]


    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    # metrics = test_metric.getMetrics()

    comments_list = ['"' + GUID + '"']
    test_line_list = [GUID]
    headers_list = ["GUID"]
    descriptions_list = ["Description"]

    # print(count)

    pbar = tqdm(total=len(metrics_info), position=position, desc=GUID, dynamic_ncols=True, unit='MI_test', ascii=' #', leave=False)

    for metric_info in metrics_info:
        time.sleep(0.05)
        pbar.update(1)



        # metric_info = test_metric.processFunction(test_metric.getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
        # metric_info = getMetricInfo(metric["@id"])
        principle = metric_info["principle"].rsplit('/', 1)[-1]
        description = metric_info["description"]

        pbar.set_description('[' + str(count) + '/' + str(total) + ']' + ' Test [' + principle + '] for [' + GUID + ']')

        # if True:
        # if principle[0:2] != 'I2':
        if principle[0:2] == 'F1':
            if PRINT_DETAILS:
                # print informations related to the metric
                printMetricInfo(metric_info)

            # evaluate the metric
            metric_evaluation_result = test_metric.processFunction(test_metric.testMetric, [metric_info["smarturl"], data], 'Evaluating metric... ')

            if PRINT_DETAILS:
                #print results of the evaluation
                printTestMetricResult(metric_evaluation_result, test_time)

            # get the score
            score = metric_evaluation_result[0]['http://semanticscience.org/resource/SIO_000300'][0]['@value']
            score = str(int(float(score)))

            # get and write comment
            comment = metric_evaluation_result[0]['http://schema.org/comment'][0]['@value']
            # remove empty lines from the comment
            comment = test_metric.cleanComment(comment)
            comment = '"' + comment + '"'
            comments_list.append(comment)



            test_line_list.append(score)
            headers_list.append(principle)
            descriptions_list.append(description)

        # GLOBAL_PBAR.refresh()


    time.sleep(0.5)
    multi_progress.release_position(position_holders, position)


    dirpath = os.path.dirname(os.getcwd() + "/" + os.path.basename(FILENAME.split("-")[0]))
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    output = OUTPUT_DIR + "/" + os.path.basename(FILENAME).replace(".txt", ".tsv")
    test_metric.writeScoreFile("\t".join(headers_list), "\t".join(test_line_list), dirpath + "/" + output)

    # write comments
    comments_filename = os.path.basename(FILENAME).split("_")[0] + "_comments.tsv"
    # test_metric.writeLineToFile("\t".join(comments_list), "\t".join(headers_list), "\t".join(descriptions_list), OUTPUT_DIR + "/" + comments_filename)



# def writeComments(comments_dict, GUID):
#     comments_filename = os.path.basename(FILENAME).split("_")[0] + "_comments"
#     if not os.path.isdir(OUTPUT_DIR):
#         os.makedirs(OUTPUT_DIR)
#     with open(OUTPUT_DIR + "/" + comments_filename, "w") as file:
#         for key in comments_dict.keys():
#             file.write(">" + key + "\n")
#             file.write(comments_dict[key])

def subsetDOIs(dois_list, nb_dois_to_select):
    new_dois_list = []
    total_nb_dois = len(dois_list)
    for i, dois in enumerate(dois_list):
        if total_nb_dois > nb_dois_to_select:
            if i % int(total_nb_dois/nb_dois_to_select) == 0 and i != 0:
                new_dois_list.append(dois)
        else:
            new_dois_list.append(dois)
    return new_dois_list



if __name__ == "__main__":
    # print("start the output")
    #
    # with output(initial_len=3, interval=0) as output_lines:
    #     while True:
    #         output_lines[0] = "First_line  {}...".format(random.randint(1,10))
    #         output_lines[1] = "Second_line {}...".format(random.randint(1,10))
    #         output_lines[2] = "Third_line  {}...".format(random.randint(1,10))
    #         time.sleep(0.5)

    # FILENAME = sys.argv[1]
    FILENAME = "./input/pangaea_dataset_dois.txt"
    data = readDOIsFile(FILENAME)


    dois_list = data.split("\n")
    dois_list = subsetDOIs(dois_list, NUMBER_DOIS)

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
    print("\n")
