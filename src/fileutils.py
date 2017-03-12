# -*- coding: utf-8 -*-
import os
import sys
import glob

# pylint: disable=C0103
class FileUtils(object):
    """
        Fileutils class
    """
    @staticmethod
    def sequential(file):
        """
            @param {pathlib.Path} file
            @return {pathlib.Path}
            exsample)exists file
                exsample.png
                exsample(1).png
                exsample(2).png
                exsample(n).png
        """
        i = 0
        basePath = file
        while file.exists():
            i += 1
            file = file.with_name('{0}({1}){2}'.format(basePath.stem, i, basePath.suffix))
            if sys.maxsize == i:
                break
        return file
    @staticmethod
    def search(target, suffixes):
        """
            file search
            @param {string}target Directory
                   {list}suffix
            @yield media
        """
        for suffix in suffixes:
            for media in glob.iglob(os.path.join(target, suffix)):
                yield media
