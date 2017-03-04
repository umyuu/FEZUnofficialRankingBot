# -*- coding: utf-8 -*-
import sys
import os

testPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if not (testPath in sys.path):
    sys.path.insert(0, testPath)
