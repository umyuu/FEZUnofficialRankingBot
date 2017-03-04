# -*- coding: utf-8 -*-
import sys
import os

basePath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
for path in [basePath , os.path.join(basePath, 'src')]:
    if not (path in sys.path):
        sys.path.insert(0, path)
