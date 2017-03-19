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
from events import SimpleEvent
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

    def get_Executor(self, max_workers):
        return ThreadPoolExecutor(max_workers=max_workers)

    @functools.lru_cache(maxsize=4)
    def getSuffix(self, content_type, suffix='.html'):
        """
            @param {string} contentType
                   {string} suffix
            @return suffix
            for example)
            ContentType -> suffix
            in:text/html; charset=utf-8         out:.html
            in:image/png                        out:.png
        """
        m = self.comp.search(content_type)
        if m is not None:
            return '.' + m.group(1)
        logger.error(content_type)
        return suffix

    def getURLs(self):
        """
            @yield URL
        """
        with open(self.file_list, 'r', encoding=self.file_list_encoding) as f:
            for line in f:
                text = line.rstrip('\n')
                if not text.startswith('http'):
                    continue
                if self.htmllink is not None:
                    link = self.htmllink
                    self.htmllink = None
                    yield link
                    continue
                yield text

    def parselink(self):
        return None

    def request(self):
        """
           internet -- (Get) --> local
           use PoolExecutor
        """
        count = 0
        with self.get_Executor(self.max_workers) as executor:
            future_to_url = {executor.submit(self.get, url, self.timeout): url for url in self.getURLs()}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    basename = os.path.basename(url)
                    buffer, contentType = future.result()
                    self.save_file(buffer, contentType, basename)
                    count += 1
                except Exception as ex:
                    logger.exception(ex)
        if count == 0:
            logger.warning('input:%s Empty', self.file_list)

    def onDownloadComplete(self, buffer):
        pass

    def save_file(self, buffer, contentType, basename):
        """
            for example)
            1)http://www.example.co.jp/Netzawar.png => Netzawar.png
            2)http://www.example.co.jp/ => example.suffix
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
