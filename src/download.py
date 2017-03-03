# -*- coding: utf-8 -*-
from logging import getLogger
import os
import sys
import tempfile
import re
from pathlib import Path
import functools
#
import requests

logger = getLogger('myapp.tweetbot')

class download(object):
    def __init__(self, config):
        self.dataDir = config['WORK_DIRECTORY']['UPLOAD']
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.file_list = config['DOWNLOAD']['FILE_LIST']
        self.file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
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
                    self.htmllink = None;
                    yield link
                yield text
    @functools.lru_cache(maxsize=4)
    def getSuffix(self, contentType, suffix='.html'):
        """
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
        count = 0
        headers = {'User-Agent': self.user_agent}
        for address in self.requestList():
            count += 1
            #if contentType.startswith('image'):
            self.get(address, headers)

        if count == 0:
            logger.warning('input:{0} Empty'.format(self.file_list))
    def sequential(self, file):
        """
            exsample)exists file
                exsample.png
                exsample(1).png
                exsample(2).png
                exsample(n).png
        """
        i = 0;
        basePath = file
        while file.exists():
            i += 1
            file = file.with_name('{0}({1}){2}'.format(basePath.stem, i, basePath.suffix))
            if sys.maxsize == i:
                break
        return file
    def get(self, address, headers):
        logger.info('download:{0}'.format(address))
        basename = os.path.basename(address)
        r = requests.get(address, headers=headers)
        contentType = r.headers['content-type']
        logger.info('content-type:{0},decode:{1}'.format(contentType, self.getSuffix(contentType)))
        with tempfile.NamedTemporaryFile(dir=self.dataDir, delete=False) as temp:
            temp.write(r.content)
            temp_file_name = temp.name
            if len(basename) == 0:
                logger.warning('create_filename:{0}'.format(os.path.basename(temp.name)))
                basename = os.path.basename(temp_file_name) + self.getSuffix(contentType)
            p = Path(self.dataDir, basename)
            p = self.sequential(p)
            
        os.replace(temp_file_name, str(p))