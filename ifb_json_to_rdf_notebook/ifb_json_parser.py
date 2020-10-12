#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

def readJsonFile(filename):
    f = open(filename, "r")
    str_content = f.read()
    ifb_json_content = json.loads(str_content)

    return ifb_json_content

if __name__ == "__main__":
    ifb_json_content = readJsonFile("ifb_content.json")

    for elem in ifb_json_content:
        print(elem.keys())
