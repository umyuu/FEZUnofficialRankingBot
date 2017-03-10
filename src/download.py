# -*- coding: utf-8 -*-
"""
    download.py
"""
from logging import getLogger
import os
from io import BytesIO
import tempfile
import re
from pathlib import Path
import functools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
#
import requests
#
from fileutils import FileUtils

# pylint: disable=C0103
logger = getLogger('myapp.tweetbot')

class Download(object):
    """
        Download　Links.
            DownloadList.txt
        use requests#get
    """
    def __init__(self, config):
        self.dataDir = config['WORK_DIRECTORY']['UPLOAD']
        entry = config['DOWNLOAD']['FILE_LIST']
        self.file_list = entry['NAME']
        self.file_list_encoding = entry['ENCODING']
        entry = config['DOWNLOAD']['REQUEST']
        self.timeout = entry['TIMEOUT']
        self.max_workers = entry['MAX_WORKERS']
        self.http_headers = {'User-Agent': config['DOWNLOAD']['USER_AGENT']}
        self.comp = re.compile(r'/(\w+);?')
        self.htmllink = None
    def getURLs(self):
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
    @functools.lru_cache(maxsize=4)
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
           use PoolExecutor
        """
        count = 0
        with self.get_Executor() as executor:
            future_to_url = {executor.submit(self.get, url, self.timeout): url for url in self.getURLs()}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    basename = os.path.basename(url)
                    buffer, contentType = future.result()
                    self.save_file(buffer, contentType, basename)
                    count += 1
                except Exception as ex:
                    logger.info('%r http_download an exception: %s' % (url, ex))
        if count == 0:
            logger.warning('input:%s Empty', self.file_list)
    def save_file(self, buffer, contentType, basename):
        """
            exsample)
            1)http://www.exsample.co.jp/Netzawar.png => Netzawar.png
            2)http://www.exsample.co.jp/ => exsample.suffix
                .suffix := self.getSuffix
            @param  {io.BytesIO}buffer Response#content
                    {string}contentType
                    {string}basename
        """
        suffix = self.getSuffix(contentType)
        logger.info('content-type:%s,decode:%s', contentType, suffix)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(buffer.getvalue())
            temp_file_name = temp.name
            if len(basename) == 0:
                logger.warning('create_filename:%s', os.path.basename(temp.name))
                basename = os.path.basename(temp_file_name)
            p = Path(self.dataDir, basename).with_suffix(suffix)
            p = FileUtils.sequential(p)

        os.replace(temp_file_name, str(p))
    def get(self, url, timeout):
        """
            call requests#get
            @param  {string}url
                    {int}timeout
            @return {io.BytesIO},{string}contentType
        """
        logger.info('download:%s', url)
        r = requests.get(url, headers=self.http_headers, timeout=timeout)
        return BytesIO(r.content), r.headers['content-type']
    def get_Executor(self):
        return ThreadPoolExecutor(max_workers=self.max_workers)
