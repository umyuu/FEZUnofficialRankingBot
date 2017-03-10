# -*- coding: utf-8 -*-
"""
    download.py
"""
from logging import getLogger
import os
from io import BytesIO
import sys
import tempfile
import re
from pathlib import Path
import functools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
#
import requests
#
from fileutils import FileUtils

logger = getLogger('myapp.tweetbot')

class Download(object):
    """
        Download　Links.
            DownloadList.txt
        use requests#get
    """
    def __init__(self, config):
        self.dataDir = config['WORK_DIRECTORY']['UPLOAD']
        self.http_headers = {'User-Agent': config['DOWNLOAD']['USER_AGENT']}
        file_list = config['DOWNLOAD']['FILE_LIST']
        self.file_list = file_list['NAME']
        self.file_list_encoding = file_list['ENCODING']
        self.comp = re.compile(r'/(\w+);?')
        self.htmllink = None
    def requestList(self):
        """
            @yield URL
        """
        with open(self.file_list, 'r', encoding=self.file_list_encoding) as f:
            for line in f:
                text = line.rstrip('\n')
                if not text.startswith('http'):
                    #logger.warning(text)
                    continue
                if self.htmllink is not None:
                    link = self.htmllink
                    self.htmllink = None
                    yield link
                    continue
                yield text
    #@functools.lru_cache(maxsize=4)
    def getSuffix(self, contentType, suffix='.html'):
        """
            @param {string} contentType
                   {string} suffix
            @return suffix
            exsample)
            ContentType -> suffix
            in:text/html; charset=utf-8         out:.html
            in:image/png                        out:.png
        """
        m = self.comp.search(contentType)
        if not m is None:
            return '.' + m.group(1)
        logger.error(contentType)
        return suffix
    def parselink(self):
        return None
    def request(self):
        """
           internet -- (Get) --> local
        """
        count = self.parallels()
        if count == 0:
            logger.warning('input:%s Empty', self.file_list)
    def save_file(self, buffer, contentType, basename):
        suffix = self.getSuffix(contentType)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(buffer.getvalue())
            temp_file_name = temp.name
            if len(basename) == 0:
                logger.warning('create_filename:%s', os.path.basename(temp.name))
                basename = os.path.basename(temp_file_name)
            p = Path(self.dataDir, basename).with_suffix(suffix)
            p = FileUtils.sequential(p)

        os.replace(temp_file_name, str(p))
    def sequential(self, file):
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
    def get(self, address, timeout):
        """
            HTTP GET
            @param  {string}address request addres
                    {int}timeout
            @return {io.BytesIO}
        """
        logger.info('download:%s', address)
        r = requests.get(address, headers=self.http_headers, timeout=timeout)
        contentType = r.headers['content-type']
        logger.info('content-type:%s,decode:%s', contentType, self.getSuffix(contentType))
        return BytesIO(r.content), contentType
    def parallels(self):
        count = 0
        with self.get_Executor() as executor:
            future_to_url = {executor.submit(self.get, url, 60): url for url in self.requestList()}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    basename = os.path.basename(url)
                    buffer, contentType = future.result()
                    self.save_file(buffer, contentType, basename)
                    count += 1
                except Exception as ex:
                    print('%r http_download an exception: %s' % (url, ex))
        return count
    def get_Executor(self):
        return ThreadPoolExecutor(max_workers=5)