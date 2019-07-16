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

TIMEOUT = (10, 300)

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

    # if json_result['type'] == 'outil':
    #     for key in json_result:
    #         print(key)
    #         print(json_result[key])

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


    if 'type' in json_result and json_result['type'] == 'plateforme':
        return True
    return False

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

            "und": "http://adefinir/",

            "toolName": "edam:data_1190",
            "platformName": "schema:name",
        }
    }

    return ctx

def rdfize(json_result):

    jld = json.loads("{}")
    jld.update(createContext())
    # jld['@id'] = str("ifbn:" + json_result['nid'])
    jld['@id'] = str("ifb:" + json_result['path']['alias'])



    for key in json_result:


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

        # alias
        # if json_result['path']:
        #     if not 'path' in jld.keys():
        #         jld['dc:alternative'] = ["ifb:" + json_result['path']['alias']]
        #     else :
        #         jld['dc:alternative'].append("ifb:" + json_result['path']['alias'])
        #


    raw_jld = json.dumps(jld)
    readRDF(raw_jld)

def platformRdf(key, json_result, jld):

    jld['@type'] = "schema:LaboratoryScience"

    # platformname
    if key == "title":
        if not 'platformName' in jld.keys():
            jld['platformName'] = [json_result['title']]
        else :
            jld['platformName'].append(json_result['title'])

    # website
    if key == "field_website":
        # hasSite ne correspond pas a un site web (a changer)
        if not 'org:hasSite' in jld.keys():
            jld['org:hasSite'] = {
                "@type": "schema:WebSite",
                "schema:url": [json_result['field_website']['fr'][0]['url']],
                "schema:name": [json_result['field_website']['fr'][0]['title']]
            }
            # jld['schema:WebSite'] = [{ "name": json_result['field_website']['fr'][0]['title']}]
        else:
            jld['org:hasSite']['schema:url'].append(json_result['field_website']['fr'][0]['url'])
            jld['org:hasSite']['schema:name'].append(json_result['field_website']['fr'][0]['title'])

    # addresse postale
    if key == "field_adresse_postal":
        if not 'org:siteAddress' in jld.keys():
            jld['org:siteAddress'] = {
                "@type": "schema:PostalAddress",
                "schema:addressCountry": [json_result['field_adresse_postal']['und'][0]['country']],
                "schema:addressLocality": [json_result['field_adresse_postal']['und'][0]['locality']],
                "schema:postalCode": [json_result['field_adresse_postal']['und'][0]['postal_code']],
                "schema:streetAddress": [json_result['field_adresse_postal']['und'][0]['thoroughfare']],
                "schema:postOfficeBoxNumber": [json_result['field_adresse_postal']['und'][0]['premise']],
            }

    # structure (node mort)
    if key == "field_stucture":
        if not 'org:Organization' in jld.keys():
            jld['org:Organization'] = {
                "@type": "org:Organization",
                "schema:identifier": [json_result['field_stucture']['und'][0]['target_id']],

            }

def toolRdf(key, json_result, jld):

    # ajouter la bonne ref
    jld['@type'] = "schema:SoftwareApplication"

    # toolname
    if key == "title":
        if not 'toolName' in jld.keys():
            jld['toolName'] = [json_result['title']]
        else :
            jld['toolName'].append(json_result['title'])

    # Description
    if key == 'field_outils_description' and json_result['field_outils_description']['en']:
        if not 'field_outils_description' in jld.keys():
            jld['dc:description'] = [json_result['field_outils_description']['en'][0]['value']]
        else :
            jld['dc:description'].append(json_result['field_outils_description']['en'][0]['value'])

    # url
    if key == 'field_lien_vers_l_outil':
        if not 'field_lien_vers_l_outil' in jld.keys():
            jld['schema:url'] = [json_result['field_lien_vers_l_outil']['und'][0]['url']]
        else :
            jld['schema:url'].append(json_result['field_lien_vers_l_outil']['und'][0]['url'])



def timestampToIso(timestamp):
    # print(time.tzname)
    tz = pytz.timezone(time.tzname[0])

    return datetime.fromtimestamp(int(timestamp), tz).isoformat()

def readRDF(raw_jld):
    """
    Open and parse RDF document.
    """

    g = rdflib.Graph()
    result = g.parse(data=raw_jld, format='json-ld')


    rdf_string = g.serialize(format="json-ld").decode("utf-8")
    # print(g.serialize(format="json-ld").decode("utf-8"))
    print(rdf_string)





if __name__ == "__main__":

    platforms_node_list = []

    # prepare connection / login informations
    name = ifb_logs.getName()
    password = ifb_logs.getPassword()
    payload = {'name': name, 'pass': password, 'form_id': 'user_login', 'op': 'Log in'}

    # opening a session
    with requests.Session() as s:

        #log in user
        print("Opening IFB session...")
        while True:
            try:
                p = s.post('https://www.france-bioinformatique.fr/user', data=payload, timeout=TIMEOUT)
                print("Connected !")
                break
            except requests.exceptions.ConnectionError as e:
                print(str(e) + "\nRetrying...")
                time.sleep(10)


        for i in range(324, 325):
            # if i < 320:
            #     continue
            print("Requesting node " + str(i) + " ...")
            json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/' + str(i) + '/node_export/json', s)
            if not json_result:
                continue
            # json_result = requestsIFB('https://www.france-bioinformatique.fr/fr/node/324/node_export/json')
            print("################## " + json_result['type'])
            if json_result['type'] == 'outil' or json_result['type'] == 'plateforme':
                rdfize(json_result)
            if getNodeInfo(json_result):
                print(i)
                platforms_node_list.append(i)

    print(platforms_node_list)
