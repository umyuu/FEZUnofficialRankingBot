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

class Serializer(object):
    @staticmethod
    def load_json(filename, encoding='utf-8-sig'):
        """
            load json data
            @param {string} filename
                   {string} encoding file encoding
            @return {dict} data
        """
        data = dict()
        with open(filename, 'r', encoding=encoding) as file:
            data = json.load(file)
        return data
    @staticmethod
    def load_ini(filename, encoding='utf-8-sig'):
        """
            load ini data.
            @param {string} filename
                   {string} encoding file encoding
            @return {config} data
        """
        data = configparser.ConfigParser()
        with open(filename, 'r', encoding=encoding) as file:
            data.read_file(file)
        return data
    @staticmethod
    def load_csv(filename, delimiter='\t', encoding='utf-8-sig', skip_header=1):
        """
            load csv data.
                limit csv.field_size_limit()
            @param {string} filename
                   {string} delimiter
                   {string} encoding file encoding
                   {int} skip_header
            @return {list} data
        """
        csv_data = []
        with open(filename, 'r', encoding=encoding) as file:
            reader = csv.reader(file, delimiter=delimiter)
            for i in range(skip_header):
                next(reader)
            for row in reader:
                csv_data.append(row)
        return csv_data
    @staticmethod
    def load_np(filename, delimiter='\t', dtype=np.float, skip_header=1):
        """
            load genfromtxt
            @param {string}    filename
                   {string}    delimiter
                   {np.dtype}  dtype
                   {int}       skip_header
            @return {np.array}
        """
        return np.genfromtxt(filename, delimiter=delimiter, dtype=dtype, skip_header=skip_header)
    @staticmethod
    def open_stream(filename, mode='w',encoding='utf-8-sig'):
        """
            @param {string} filename
                   {string} mode
                   {string} encoding
            @return {file}
        """
        return open(filename, mode, encoding=encoding)
