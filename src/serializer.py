# -*- coding: utf-8 -*-
"""
    serializer.py
    load file type.
        json
        ini
"""
import json
import configparser
import csv

def load_json(filename, encoding='utf-8-sig'):
    """
        load json data
        @params filename load path.
                encoding file encoding
        @return data
    """
    json_data = dict()
    with open(filename, 'r', encoding=encoding) as file:
        json_data = json.load(file)
    return json_data

def load_ini(filename, encoding='utf-8-sig'):
    """
        load ini data.
        @params filename load path.
                encoding file encoding.
        @return data
    """
    config = configparser.ConfigParser()
    with open(filename, 'r', encoding=encoding) as file:
        config.read_file(file)
    return config

def load_csv(filename, encoding='utf-8-sig'):
    """
        load csv data.
        @params filename load path.
                encoding file encoding.
        @return data
    """
    csv_data = []
    with open(filename, 'r', encoding=encoding) as file:
        reader = csv.reader(file)
        #header = next(reader)
        for row in reader:
            csv_data.append(row)
    return csv_data
