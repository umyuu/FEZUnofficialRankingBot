# -*- coding: utf-8 -*-
"""
    serializer.py
    load file type.
        json
        ini
"""
import json
import configparser

def load_json(filename, encoding='utf-8-sig'):
    """
        filed load json data
        @params filename load path.
                encoding file encoding
        @return json data
    """
    json_data = dict()
    with open(filename, encoding=encoding) as file:
        json_data = json.load(file)
    return json_data

def load_ini(filename, encoding='utf-8-sig'):
    """
        load configure.
        @params filename load path.
                encoding file encoding.
        @return ini data
    """
    config = configparser.ConfigParser()
    with open(filename, 'r', encoding=encoding) as file:
        config.read_file(file)
    return config
