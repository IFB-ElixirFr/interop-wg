#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
import json
import simplejson

import ifb_logs
import time
from rdflib.namespace import RDF
import rdflib

import pytz
from datetime import datetime
from time import gmtime, strftime

from bs4 import BeautifulSoup

import multiprocessing
from multiprocessing import Pool, freeze_support, RLock, Lock, Array, Manager

import sys
import os

TIMEOUT = (10, 300)
LANGUAGE = "en"
RDF_FORMAT = "turtle"

def requestsIFB(url, s):

    while True:
        try:
            # An authorised request.
            r = s.get(url, timeout=TIMEOUT).json()
            # print(s.get(url).status_code)
                # etc...
            print("Done")
            break
        except simplejson.errors.JSONDecodeError:
            print("No JSON found...")
            return False
        except requests.exceptions.ConnectionError as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)


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



def createContext():

    ctx = {
        "@context": {
            "edam": "http://edamontology.org/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "schema": "http://schema.org/",
            "dc": "http://purl.org/dc/terms/",
            "ifbn": "https://www.france-bioinformatique.fr/node/",
            "ifb": "https://www.france-bioinformatique.fr/",
            "org": "http://www.w3.org/ns/org#",
            "vcard": "https://www.w3.org/TR/vcard-rdf/",
            "dfcore": "http://ontology.tno.nl/dfcore/",
            "dbpedia": "http://dbpedia.org/ontology/",
            "gleif-base": "https://www.gleif.org/ontology/Base/",
            "premis": "http://sw-portal.deri.org/ontologies/swportal#",
            "dbpedia-owl": "http://dbpedia.org/ontology/",

            "und": "http://adefinir/",

            "toolName": "edam:data_1190",
            "trainingMaterial": "edam:data_3669",
        }
    }

    return ctx

def rdfize(json_result):

    jld = json.loads("{}")
    jld.update(createContext())
    # jld['@id'] = str("ifbn:" + json_result['nid'])
    jld['@id'] = str("ifb:" + json_result['path']['alias'])



    for key in json_result:

        # field contain a list if empty, otherwise its a string or dict value
        if type(json_result[key]) is list:
            continue

        # creation time
        if key == 'created':
            if not 'created' in jld.keys():
                jld['dc:created'] = [timestampToIso(json_result['created'])]
            else :
                jld['dc:created'].append([timestampToIso(json_result['created'])])

        # changed time
        if key == 'changed':
            if not 'changed' in jld.keys():
                jld['dc:modified'] = [timestampToIso(json_result['changed'])]
            else :
                jld['dc:modified'].append([timestampToIso(json_result['changed'])])

        if json_result['type'] == 'outil':
            toolRdf(key, json_result, jld)

        if json_result['type'] == 'plateforme':
            platformRdf(key, json_result, jld)

        if json_result['type'] == 'formation':
            formationRDF(key, json_result, jld)

        # alias
        # if json_result['path']:
        #     if not 'path' in jld.keys():
        #         jld['dc:alternative'] = ["ifb:" + json_result['path']['alias']]
        #     else :
        #         jld['dc:alternative'].append("ifb:" + json_result['path']['alias'])
        #


    raw_jld = json.dumps(jld)
    return raw_jld


def formationRDF(key, json_result, jld):

    jld['@type'] = "trainingMaterial"
    language = "en"

    # title
    if key == "title":
        if not 'schema:name' in jld.keys():
            jld['schema:name'] = [json_result['title']]
        else :
            jld['schema:name'].append(json_result['title'])

    # type de formation
    if key == 'field_type_de_formation' and language in json_result['field_type_de_formation'].keys():
        for i, elem in enumerate(json_result['field_type_de_formation'][language]):
            if not 'dc:educationLevel' in jld.keys():
                jld['dc:educationLevel'] = [elem['value']]
            else :
                jld['dc:educationLevel'].append(elem['value'])

    # Description
    if key == 'field_description' and language in json_result['field_description'].keys():
        for i, elem in enumerate(json_result['field_description'][language]):
            if not 'dc:description' in jld.keys():
                jld['dc:description'] = [elem['value']]
            else :
                jld['dc:description'].append(elem['value'])

    # location
    if key == 'field_field_lieu_de_la_formation':
        for i, elem in enumerate(json_result['field_field_lieu_de_la_formation']['und']):
            if not 'dbpedia:location' in jld.keys():
                jld['dbpedia:location'] = [elem['value']]
            else :
                jld['dbpedia:location'].append(elem['value'])

    # url
    if key == 'field_lien_vers_la_formation':
        for i, elem in enumerate(json_result['field_lien_vers_la_formation']['und']):
            if not 'schema:url' in jld.keys():
                jld['schema:url'] = [elem['url']]
            else :
                jld['schema:url'].append(elem['url'])




def platformRdf(key, json_result, jld):


    jld['@type'] = "schema:LaboratoryScience"
    language = LANGUAGE

    # platformname
    if key == "title":
        if not 'schema:name' in jld.keys():
            jld['schema:name'] = [json_result['title']]
        else :
            jld['schema:name'].append(json_result['title'])

    # website
    if key == "field_website" and language in json_result['field_website'].keys():
        for i, elem in enumerate(json_result['field_website'][language]):
            # hasSite ne correspond pas a un site web (a changer)
            if not 'gleif-base:hasWebsite' in jld.keys():
                jld['gleif-base:hasWebsite'] = {
                    "@type": "schema:WebSite",
                    "schema:url": [elem['url']],
                    "schema:name": [elem['title']]
                }
                # jld['schema:WebSite'] = [{ "name": json_result['field_website']['fr'][0]['title']}]
            else:
                jld['org:hasSite']['schema:url'].append(json_result['field_website'][language][i]['url'])
                jld['org:hasSite']['schema:name'].append(json_result['field_website'][language][i]['title'])

    # addresse postale
    if key == "field_adresse_postal":
        for i, elem in enumerate(json_result['field_adresse_postal']['und']):
            if not 'org:siteAddress' in jld.keys():
                jld['org:siteAddress'] = {
                    "@type": "schema:PostalAddress",
                    "schema:addressCountry": [elem['country']],
                    "schema:addressLocality": [elem['locality']],
                    "schema:postalCode": [elem['postal_code']],
                    "schema:streetAddress": [elem['thoroughfare']],
                    "schema:postOfficeBoxNumber": [elem['premise']],
                }
            else:
                jld['org:siteAddress']['schema:addressCountry'].append(elem['country'])
                jld['org:siteAddress']['schema:addressLocality'].append(elem['locality'])
                jld['org:siteAddress']['schema:postalCode'].append(elem['postal_code'])
                jld['org:siteAddress']['schema:streetAddress'].append(elem['thoroughfare'])
                jld['org:siteAddress']['schema:postOfficeBoxNumber'].append(elem['premise'])

    # structure (node mort)
    if key == "field_stucture":
        for i, elem in enumerate(json_result['field_stucture']['und']):
            if not 'org:Organization' in jld.keys():
                jld['org:Organization'] = {
                    "@type": "org:Organization",
                    "schema:identifier": [elem['target_id']],
                }
            else:
                jld["org:Organization"]["schema:identifier"].append(elem['target_id'])

    # outils
    if key == "field_outils":
        for i, elem in enumerate(json_result['field_outils']['und']):
            if not "premis:hasSoftware" in jld.keys():
                jld["premis:hasSoftware"] = {
                    "@type": "swpo:Tool",
                    "schema:identifier": [elem['target_id']]
                }
            else:
                jld["premis:hasSoftware"]["schema:identifier"].append(elem['target_id'])

    # données (DB ?)
    if key == "field_donnee":
        for i, elem in enumerate(json_result['field_donnee']['und']):
            if not "dbpedia-owl:Database" in jld.keys():
                jld["dbpedia-owl:Database"] = {
                    "schema:identifier": [elem['target_id']]
                }
            else:
                jld["dbpedia-owl:Database"]["schema:identifier"].append(elem['target_id'])


def toolRdf(key, json_result, jld):

    # ajouter la bonne ref
    jld['@type'] = "schema:SoftwareApplication"
    language = LANGUAGE

    # toolname
    if key == "title":
        if not 'toolName' in jld.keys():
            jld['toolName'] = [json_result['title']]
        else :
            jld['toolName'].append(json_result['title'])

    # Description
    if key == 'field_outils_description' and language in json_result['field_outils_description'].keys():
        for i, elem in enumerate(json_result['field_outils_description'][language]):
            if not 'dc:description' in jld.keys():
                jld['dc:description'] = [elem['value']]
            else :
                jld['dc:description'].append(elem['value'])

    # url
    if key == 'field_lien_vers_l_outil':
        for i, elem in enumerate(json_result['field_lien_vers_l_outil']['und']):
            if not 'schema:url' in jld.keys():
                jld['schema:url'] = [elem['url']]
            else :
                jld['schema:url'].append(elem['url'])



def timestampToIso(timestamp):
    tz = pytz.timezone(time.tzname[0])

    return datetime.fromtimestamp(int(timestamp), tz).isoformat()

def readRDF(raw_jld):
    """
    Open and parse RDF document.
    """

    g = rdflib.Graph()
    result = g.parse(data=raw_jld, format='json-ld')


    rdf_string = g.serialize(format=RDF_FORMAT).decode("utf-8")
    print(rdf_string)

def writeRDF(raw_jld, type, node_id):
    """
    Write a RDF document
    """
    g = rdflib.Graph()
    result = g.parse(data=raw_jld, format='json-ld')

    rdf_string = g.serialize(format=RDF_FORMAT).decode("utf-8")
    ts = datetime.now().timestamp()
    time = timestampToIso(ts)

    dir_path = "./" + type
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    with open(dir_path + "/" + str(node_id) + "_" + time + ".ttl"  ,"w") as file:
        file.write(rdf_string)

def getPageTitle(node_url, s):

    while True:
        try:
            # An authorised request.
            r = s.get(node_url, timeout=TIMEOUT)
            # print(s.get(url).status_code)
                # etc...
            break
        except requests.exceptions.ConnectionError as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)

    soup = BeautifulSoup(r.text, 'html.parser')
    title = str(soup.title.string)
    soup.decompose()
    return title

def parallelIfbRequest(tuple):
    i = tuple[0]
    s = tuple[1]

    # 324, 326
    # if i < 320:
    #     continue
    print("Requesting node " + str(i) + " ...")
    json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/' + str(i) + '/node_export/json', s)


    # if their is a json, rdfize it
    # if not json_result:
    #     continue
    # print("################## " + json_result['type'])
    # type_to_rdfize = ['outil', 'plateforme', 'formation']
    # if json_result['type'] in type_to_rdfize:
        # rdfize(json_result)


    # check node if they have json and their title

    title = getPageTitle("https://www.france-bioinformatique.fr/fr/node/" + str(i), s)
    if not json_result:
        # print(i)
        json_type = "no_json_export"
    else:
        json_type = json_result['type']
    # info_node_list.append((str(i), json_type, title))
    return (i, json_type, title)

def ifbAuthenticate(payload):
    while True:
        try:
            s.post('https://www.france-bioinformatique.fr/user', data=payload, timeout=TIMEOUT)
            print("Connected !")
            break
        except requests.exceptions.ConnectionError as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            print(str(e) + "\nRetrying...")
            time.sleep(10)



if __name__ == "__main__":

    info_node_list = []

    # prepare connection / login informations
    name = ifb_logs.getName()
    password = ifb_logs.getPassword()
    payload = {'name': name, 'pass': password, 'form_id': 'user_login', 'op': 'Log in'}

    # opening a session
    with requests.Session() as s:

        #log in user
        print("Opening IFB session...")
        ifbAuthenticate(payload)


        if False:
            # parallelized
            pool = multiprocessing.Pool(2)
            process_list = []
            for i in range(0, 2000):
                process_list.append((i, s))

            for result in pool.imap(parallelIfbRequest, process_list):
                info_node_list.append(result)
        else:

            #not parallelized
            # for node_id in range(0, 400):
            for node_id in range(0, 5000):
                # 324, 326

                print("Requesting node " + str(node_id) + " ...")
                json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/' + str(node_id) + '/node_export/json', s)

                # # if their is a json, rdfize it
                # if not json_result:
                #     continue
                # print("################## " + json_result['type'])
                # type_to_rdfize = ['outil', 'plateforme', 'formation']
                # # type_to_rdfize = ['plateforme']
                # if json_result['type'] in type_to_rdfize:
                #     raw_jld = rdfize(json_result)
                #     readRDF(raw_jld)
                #     writeRDF(raw_jld, json_result['type'], node_id)


                # check node if they have json and their title

                title = getPageTitle("https://www.france-bioinformatique.fr/fr/node/" + str(node_id), s)
                if not json_result:
                    json_type = "no_json_export"
                else:
                    json_type = json_result['type']
                info_node_list.append((str(node_id), json_type, title))
                print((node_id, json_type, title))

    with open("pages_info_ifb_5000", "w") as f:
        string = ""
        for (node, type, page_title) in info_node_list:
            string += node + "\t" + type + "\t" + page_title + "\n"
        f.write(string)
