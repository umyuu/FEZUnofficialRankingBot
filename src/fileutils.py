# -*- coding: utf-8 -*-
import sys

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
