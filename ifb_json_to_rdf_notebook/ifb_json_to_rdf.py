#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
import json
import simplejson
from tqdm import tqdm

import ifb_logs
import time
from rdflib.namespace import RDF
import rdflib
import pyshacl

import pytz
from datetime import datetime
from time import gmtime, strftime

from bs4 import BeautifulSoup

import multiprocessing
from multiprocessing import Pool, freeze_support, RLock, Lock, Array, Manager

import sys
import os
import logging
import logging.handlers

TIMEOUT = (10, 300)
# fr or en
LANGUAGE = "en"
# turtle or json-ld
RDF_FORMAT = "turtle"
OUTPUT_DIR = LANGUAGE + "_" + RDF_FORMAT + "_ifb_dump_test"

def requestsIFB(url, s, node_id):
    """
    Request a node on IFB website (node export to json).

    @param url String The url to request a node in json format
    @param s requests.Session Object corresponding to the connection session
    @param node_id String The node number

    @return json The result of the requested node as JSON format/object
    """
    while True:
        try:
            logger.info('[' + node_id + ']' + " Requesting: [" + url + "]")
            # An authorised request.
            r = s.get(url, timeout=TIMEOUT).json()
            # print(s.get(url).status_code)
                # etc...
            # print("Done")
            logger.info('[' + node_id + ']' + " JSON retrieved")
            break
        except simplejson.errors.JSONDecodeError:
            logger.warning('[' + node_id + ']' + " No JSON found...")
            # print("No JSON found...")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error('[' + node_id + ']' + " ConnectionError, retrying: " + str(e))
            # print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            logger.error('[' + node_id + ']' + " ReadTimeout, retrying: " + str(e))
            # print(str(e) + "\nRetrying...")
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
    """
    Create and return the context for a RDFlib object (json-ld format).

    @return dict Contains the context for a rdflib json-ld object
    """
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
            "cci": "http://cookingbigdata.com/linkeddata/ccinstances#",
            "ocds": "http://purl.org/onto-ocds/ocds#",
            "frapo": "http://purl.org/cerif/frapo/",
            "geosp": "http://rdf.geospecies.org/ont/geospecies#",
            "meb": "http://rdf.myexperiment.org/ontologies/base/",
            "wl": "http://www.wsmo.org/ns/wsmo-lite#",
            "nno": "https://w3id.org/nno/ontology#",
            "c4o": "http://purl.org/spar/c4o/",
            "dqm": "http://purl.org/dqm-vocabulary/v1/dqm#",

            # "und": "http://adefinir/",

            "toolName": "edam:data_1190",
            "trainingMaterial": "edam:data_3669",
        }
    }

    return ctx

def rdfize(json_result):
    """
    Parse the node json object from the requested node, and then, select the keys
    of interest to add them to another json object as well as RDF (json-ld - uri -markup)
    to allow the json object to be converted to a rdflib json-ld object.

    @param json_result json The result of the requested node export to json

    @return String The raw json-ld as string
    """
    jld = json.loads("{}")
    jld.update(createContext())
    # jld['@id'] = str("ifbn:" + json_result['nid'])
    jld['@id'] = str("ifb:" + json_result['path']['language'] + "/" + json_result['path']['alias'])



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
    """
    Add the values from the json export node to a new json object (jld) whose
    are specific from a formation.

    @param key String A key from the json export node object
    @param json_result json The json export node object
    @param jld json The new json object which contains json-ld markups
    """
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
    """
    Add the values from the json export node to a new json object (jld) whose
    are specific from a platform.

    @param key String A key from the json export node object
    @param json_result json The json export node object
    @param jld json The new json object which contains json-ld markups
    """

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

    # cpu hour/year
    # if key == "field_heure_de_cpu_an":
    #     for i, elem in enumerate(json_result['field_heure_de_cpu_an']['und']):
    #         if not "cci:hasCPU" in jld.keys():
    #             jld["cci:hasCPU"] = {
    #                 "schema:identifier": [elem['value']]
    #             }
    #         else:
    #             jld["cci:hasCPU"]["schema:identifier"].append(elem['value'])

    # cpu number
    if key == "field_ferme_de_calcul":
        for i, elem in enumerate(json_result['field_ferme_de_calcul']['und']):
            if not "cci:hasCPU" in jld.keys():
                jld["cci:hasCPU"] = {
                    "@type": "cci:cpu",
                    "ocds:valueAmount": [elem['value']]
                }
            else:
                jld["cci:hasCPU"]["ocds:valueAmount"].append(elem['value'])

    # expertise
    if key == "field_description_des_expertises" and language in json_result['field_description_des_expertises'].keys():
        for i, elem in enumerate(json_result['field_description_des_expertises'][language]):
            if not "frapo:hasExpertise" in jld.keys():
                jld["frapo:hasExpertise"] = {
                    "dc:description": [elem['value']]
                }
            else:
                jld["frapo:hasExpertise"]["dc:description"].append(elem['value'])



    # projets hébergés
    if key == "field_projets_h_berg_s" and language in json_result['field_projets_h_berg_s'].keys():
        for i, elem in enumerate(json_result['field_projets_h_berg_s'][language]):
            if not "geosp:hasProject" in jld.keys():
                jld["geosp:hasProject"] = {
                    "ocds:valueAmount": [elem['value']]
                }
            else:
                jld["geosp:hasProject"]["ocds:valueAmount"].append(elem['value'])

    # type d'infra
    if key == 'field_type_d_infrastructure' and language in json_result['field_type_d_infrastructure'].keys():
        for i, elem in enumerate(json_result['field_type_d_infrastructure'][language]):
            if not 'dbpedia-owl:Infrastructure' in jld.keys():
                jld['dbpedia-owl:Infrastructure'] = [elem['value']]
            else :
                jld['dbpedia-owl:Infrastructure'].append(elem['value'])

    # serveur description
    if key == 'field_descriptions_des_serveurs' and language in json_result['field_descriptions_des_serveurs'].keys():
        for i, elem in enumerate(json_result['field_descriptions_des_serveurs'][language]):
            if not 'cogs:Server' in jld.keys():
                jld['cogs:Server'] =  {
                    "dc:description": [elem['value']]
                }
            else :
                jld['cogs:Server']["dc:description"].append(elem['value'])

    # nombre utilisateurs (du serveur ?)
    if key == "field_nombre_d_utilisateurs":
        for i, elem in enumerate(json_result['field_nombre_d_utilisateurs']['und']):
            if not "meb:User" in jld.keys():
                jld["meb:User"] = {
                    "ocds:valueAmount": [elem['value']]
                }
            else:
                jld["meb:User"]["ocds:valueAmount"].append(elem['value'])

    # capacité stockage
    if key == "field_capacit_de_stockage_utile":
        for i, elem in enumerate(json_result['field_capacit_de_stockage_utile']['und']):
            if not "cci:hasStorage" in jld.keys():
                jld["cci:hasStorage"] = {
                    "@type": "cci:storage",
                    "cci:storage_size": [elem['value']]
                }
            else:
                jld["cci:hasStorage"]["cci:storage_size"].append(elem['value'])

    # aide projet
    if key == "field_description_aide_projets" and language in json_result['field_description_aide_projets'].keys():
        for i, elem in enumerate(json_result['field_description_aide_projets'][language]):
            if not "frapo:supports" in jld.keys():
                jld["frapo:supports"] = {}

            if not "dc:description" in jld["frapo:supports"].keys():
                jld["frapo:supports"].update({"dc:description": [elem['value']]})
            else:
                jld["frapo:supports"]["dc:description"].append(elem['value'])


    # conditions_d'appui
    if key == 'field_conditions_d_appui' and language in json_result['field_conditions_d_appui'].keys():
        for i, elem in enumerate(json_result['field_conditions_d_appui'][language]):
            if not "frapo:supports" in jld.keys():
                jld["frapo:supports"] = {}

            if not "wl:Condition" in jld["frapo:supports"].keys():
                jld["frapo:supports"].update({"wl:Condition": [elem['value']]})
            else:
                jld["frapo:supports"]["wl:Condition"].append(elem['value'])

    # titre appui a projet
    if key == 'field_titre_appui_a_projet' and language in json_result['field_titre_appui_a_projet'].keys():
        for i, elem in enumerate(json_result['field_titre_appui_a_projet'][language]):
            if not "frapo:supports" in jld.keys():
                jld["frapo:supports"] = {}

            if not "dc:title" in jld["frapo:supports"].keys():
                jld["frapo:supports"].update({"dc:title": [elem['value']]})
            else:
                jld["frapo:supports"]["dc:title"].append(elem['value'])






def toolRdf(key, json_result, jld):
    """
    Add the values from the json export node to a new json object (jld) whose
    are specific from a tool.

    @param key String A key from the json export node object
    @param json_result json The json export node object
    @param jld json The new json object which contains json-ld markups
    """
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

    # citation
    if key == 'field_outils_citations':
        for i, elem in enumerate(json_result['field_outils_citations']['und']):
            if not "c4o:GlobalCitationCount" in jld.keys():
                jld["c4o:GlobalCitationCount"] = [elem['value']]

            else:
                jld["c4o:GlobalCitationCount"].append(elem['value'])

    # visites annuelles
    if key == 'field_outils_visites_anuelles':
        for i, elem in enumerate(json_result['field_outils_visites_anuelles']['und']):
            if not "dbpedia-owl:visitorsPerYear" in jld.keys():
                jld["dbpedia-owl:visitorsPerYear"] = [elem['value']]
            else:
                jld["dbpedia-owl:visitorsPerYear"].append(elem['value'])

    # visites uniques /!\ à completer !!!!
    if key == 'field_outils_visites_uniques':
        for i, elem in enumerate(json_result['field_outils_visites_uniques']['und']):
            if not "dbpedia-owl:visitorsTotal" in jld.keys():
                jld["dbpedia-owl:visitorsTotal"] = [elem['value']]
            else:
                jld["dbpedia-owl:visitorsTotal"].append(elem['value'])

    # downloads
    if key == 'field_outils_telechargements':
        for i, elem in enumerate(json_result['field_outils_telechargements']['und']):
            if not "nno:hasDownloadCount" in jld.keys():
                jld["nno:hasDownloadCount"] = [elem['value']]
            else:
                jld["nno:hasDownloadCount"].append(elem['value'])

    # conditions
    if key == 'field_outils_conditions' and language in json_result['field_outils_conditions'].keys():
        for i, elem in enumerate(json_result['field_outils_conditions'][language]):
            if not 'dqm:hasCondition' in jld.keys():
                jld['dqm:hasCondition'] = {
                    "dqm:Condition": [elem['value']]
                }
            else :
                jld['dqm:hasCondition']["dqm:Condition"].append(elem['value'])

    # !!!!! following keys have almost never a value associated !!!!
    # OS
    if key == 'field_syst_me_d_exploitation':
        print("field_syst_me_d_exploitation")
        print(json_result['field_syst_me_d_exploitation'])
        # for i, elem in enumerate(json_result['field_syst_me_d_exploitation']['und']):
        #     if not "nno:hasDownloadCount" in jld.keys():
        #         jld["nno:hasDownloadCount"] = [elem['value']]
        #     else:
        #         jld["nno:hasDownloadCount"].append(elem['value'])
    # prerequis
    if key == 'field_pr_requis_d_utilisation':
        print("field_pr_requis_d_utilisation")
        print(json_result['field_pr_requis_d_utilisation'])

    # version logiciel
    if key == 'field_version_du_logiciel':
        print("field_version_du_logiciel")
        print(json_result['field_version_du_logiciel'])

    # type logiciel
    if key == 'field_type_de_logiciel':
        print("field_type_de_logiciel")
        print(json_result['field_type_de_logiciel'])

    # licence
    if key == 'field_license':
        print("field_license")
        print(json_result['field_license'])


    # contact support
    if key == 'field_contact_du_support_de_l_ou':
        print("field_contact_du_support_de_l_ou")
        print(json_result['field_contact_du_support_de_l_ou'])

def timestampToIso(timestamp):
    """
    Convert a time stamp date to a ISO formated date.

    @param timestamp int A date timestamp

    @return String A date ISO formated
    """
    tz = pytz.timezone(time.tzname[0])

    return datetime.fromtimestamp(int(timestamp), tz).isoformat()

def readRDF(raw_jld):
    """
    Read a rdf string (json-ld there) and convert it to a specific RDF format to display it.

    @param raw_jld String A string in json-ld format
    """

    g = rdflib.Graph()
    result = g.parse(data=raw_jld, format='json-ld')


    rdf_string = g.serialize(format=RDF_FORMAT).decode("utf-8")
    print(rdf_string)

def writeRDF(raw_jld, type, node_id):
    """
    Read a rdf string (json-ld there) and convert it to a specific RDF format to
    write it to a file.

    @param raw_jld String A string in json-ld format
    @param type String The type of the IFB ressource (formation, tool, platform, etc)
    @param node_id String The node id corresponding to the ressource (from IFB website)
    """
    g = rdflib.Graph()
    result = g.parse(data=raw_jld, format='json-ld')

    rdf_string = g.serialize(format=RDF_FORMAT).decode("utf-8")
    if verifyGraph(g):
        ts = datetime.now().timestamp()
        time = timestampToIso(ts)

        dir_path = OUTPUT_DIR + "/" + type
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        file_path = dir_path + "/" + str(node_id) + "_" + time + ".ttl"
        with open(file_path  ,"w") as file:
            file.write(rdf_string)
        logger.info('[' + str(node_id) + ']' + " Graph created and valid, file path: [" + file_path + "]")
    else:
        if not os.path.isdir(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        logger.error('[' + str(node_id) + ']' + " Graph is not valid, no result file created")


def verifyGraph(g):
    """
    Validate the rdflib graph with shacl.

    @param g rdflib.Graph The graph of the new json-ld

    @return bool Is the json-ld valid or not
    """
    r = pyshacl.validate(g)
    conforms, results_graph, results_text = r
    return conforms

def getPageTitle(node_url, s):
    """
    Retrieve the title (from html) of a IFB node page.

    @param node_url String The url of the node
    @param s requests.Session Object corresponding to the connection session

    @return String The title of the web page
    """
    while True:
        try:
            # An authorised request.
            r = s.get(node_url, timeout=TIMEOUT)
            # print(s.get(url).status_code)
                # etc...
            break
        except requests.exceptions.ConnectionError as e:
            # print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            # print(str(e) + "\nRetrying...")
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
    """
    Connect and open a session on IFB website using payload connection informations.
    keys: name, pass, form_id, op.

    @param payload dict The necessaries informations to open a session on IFB website
    """
    while True:
        try:
            logger.info('Connecting to IFB website...')
            s.post('https://www.france-bioinformatique.fr/user', data=payload, timeout=TIMEOUT)
            logger.info('Connected')
            print("Connected !")
            break
        except requests.exceptions.ConnectionError as e:
            logger.error("ConnectionError, retrying: " + str(e))
            print(str(e) + "\nRetrying...")
            time.sleep(10)
        except requests.exceptions.ReadTimeout as e:
            logger.error(" ReadTimeout, retrying: " + str(e))
            print(str(e) + "\nRetrying...")
            time.sleep(10)

def setupCustomLogger(name, filename):
    """
    @param name String The name of the logger
    @param filename String The filename

    @return A logger object
    """
    formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(filename, mode='w')
    handler.setFormatter(formatter)
    # screen_handler = logging.StreamHandler(stream=sys.stdout)
    # screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # logger.addHandler(screen_handler)
    return logger

if __name__ == "__main__":

    # info_node_list = []

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    logger = setupCustomLogger('rdfize_ifb', OUTPUT_DIR + '/dump_log')

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
            nodes_list = range(0, 5000)
            nodes_pbar = tqdm(nodes_list, position=1)
            for node_id in nodes_pbar:
                # 324, 326
                node_id = str(node_id)
                nodes_pbar.set_description('Processing node [' + node_id + ']')

                # print("Requesting node " + str(node_id) + " ...")
                json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/' + node_id + '/node_export/json', s, node_id)

                # if their is a json, rdfize it
                if not json_result:
                    continue
                # print("################## " + json_result['type'])
                type_to_rdfize = ['outil', 'plateforme', 'formation']
                # type_to_rdfize = ['plateforme']
                if json_result['type'] in type_to_rdfize:
                    logger.info('[' + node_id + ']' + " Type: [" + json_result['type'] + "], rdfize: [True]")
                    raw_jld = rdfize(json_result)
                    # readRDF(raw_jld)
                    writeRDF(raw_jld, json_result['type'], node_id)
                else:
                    logger.warning('[' + node_id + ']' + " Type: [" + json_result['type'] + "], rdfize: [False]")
    print("\n\n\nDump done !")
                # check node if they have json and their title

    #             title = getPageTitle("https://www.france-bioinformatique.fr/fr/node/" + str(node_id), s)
    #             if not json_result:
    #                 json_type = "no_json_export"
    #             else:
    #                 json_type = json_result['type']
    #             info_node_list.append((str(node_id), json_type, title))
    #             print((node_id, json_type, title))
    #
    # with open("pages_info_ifb_5000", "w") as f:
    #     string = ""
    #     for (node, type, page_title) in info_node_list:
    #         string += node + "\t" + type + "\t" + page_title + "\n"
    #     f.write(string)
