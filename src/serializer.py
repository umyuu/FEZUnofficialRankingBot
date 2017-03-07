# -*- coding: utf-8 -*-
"""
    serializer.py
    load file type.
        json / ini / csv / numpy
"""
import json
import configparser
import csv
#
import numpy as np

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

def load_csv(filename, encoding='utf-8-sig', skip_header=1):
    """
        load csv data.
        @params filename load path.
                encoding file encoding.
        @return data
    """
    csv_data = []
    with open(filename, 'r', encoding=encoding) as file:
        reader = csv.reader(file)
        for i in range(skip_header):
            next(reader)
        for row in reader:
            csv_data.append(row)
    return csv_data
def load_np(filename, delimiter='\t', dtype=np.float, skip_header=1):
    return np.genfromtxt(filename, delimiter=delimiter, dtype=dtype, skip_header=skip_header)
