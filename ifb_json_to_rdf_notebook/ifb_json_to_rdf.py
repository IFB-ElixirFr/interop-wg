#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
import json
import simplejson

import ifb_logs

TIMEOUT = (10, 300)

def requestsIFB(url, s):

    try:
        # An authorised request.
        r = s.get(url).json()
        # print(s.get(url).status_code)
            # etc...
    except simplejson.errors.JSONDecodeError:
        return False


    # while True:
    #     try:
    #         response = requests.post(url, timeout=TIMEOUT, data=payload)
    #         break
    #     except SSLError:
    #         time.sleep(5)
    #     except requests.exceptions.Timeout:
    #         time.sleep(5)
    #
    return r[0]

def requestsChildIFB(url):
    url = url

# http://edamontology.org/data_1190



def getNodeInfo(json_result):

    if json_result['type'] == 'outil':
        for key in json_result:
            print(key)
            print(json_result[key])

    # # en test
    # if isTypePlateform(json_result):
    #     # parse json
    #     for key in json_result:
    #         if key == 'field_outils':
    #             if not json_result[key] == []:
    #                 for i, node in enumerate(json_result[key]['und']):
    #                     node_nb = node['target_id']
    #                     json_result[key]['und'][i]['target_id'] = 'https://www.france-bioinformatique.fr/node/' + node_nb
    #
    #         if key.startswith('field_responsable_technique'):
    #             print(key)
    #             print(json_result[key])
    #
    #         if key.startswith('field_') and not json_result[key] == []:
    #             for i, node in enumerate(json_result[key]['und']):
    #                 pass
    #         return True
    return False

def isTypePlateform(json_result):
    # temporaire
    print(json_result['type'])

    if 'type' in json_result and json_result['type'] == 'plateforme':
        return True
    return False

def createPrefix():

    prefix_dict = {
                    "edam": "http://edamontology.org/",
                    "foaf": "http://xmlns.com/foaf/0.1/",
                    "schema": "http://schema.org/",
                    "dcterms": "http://purl.org/dc/terms/"
                }


if __name__ == "__main__":

    platforms_node_list = []

    # prepare connection / login informations
    name = ifb_logs.getName()
    password = ifb_logs.getPassword()
    payload = {'name': name, 'pass': password, 'form_id': 'user_login', 'op': 'Log in'}

    # opening a session
    with requests.Session() as s:
        #log in user
        p = s.post('https://www.france-bioinformatique.fr/user', data=payload)

        for i in range(270, 280):
            # if i < 320:
            #     continue
            # print(i)
            json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/' + str(i) + '/node_export/json', s)
            if not json_result:
                continue
            # json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/324/node_export/json')
            if getNodeInfo(json_result):
                print(i)
                platforms_node_list.append(i)

    print(platforms_node_list)
