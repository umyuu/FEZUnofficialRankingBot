# -*- coding: utf-8 -*-
from logging import getLogger
import os
import sys
import tempfile
import re
from pathlib import Path
# library
import requests

logger = getLogger('myapp.tweetbot')

class download():
    def __init__(self, config):
        self.data = config['WORK_FOLDER']['UPLOAD']
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.file_list = config['DOWNLOAD']['FILE_LIST']
        self.file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
        self.comp = re.compile(r'/(\w+);?')
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
                yield text
    def getSuffix(self, r, suffix='.html'):
        """
            ContentType -> suffix
            text/html; charset=utf-8
            image/png
        """
        m = self.comp.search(r.headers['content-type'])
        if not m is None:
            return '.' + m.group(1)
        #logger.error(r.headers['content-type'])
        return suffix
    def request(self):
        """
           internet -- (Get) --> local
           exsample)exists file
             exsample.png
             exsample(1).png
             exsample(2).png
             exsample(n).png
        """
        count = 0
        headers = {'User-Agent': self.user_agent}
        for address in self.requestList():
            count += 1
            logger.info('download:{0}'.format(address))
            basename = os.path.basename(address)
            r = requests.get(address, headers=headers)
            logger.info('content-type:{0},decode:{1}'.format(r.headers['content-type'], self.getSuffix(r)))
            
            with tempfile.NamedTemporaryFile(dir=self.data, delete=False) as temp:
                temp.write(r.content)
                temp_file_name = temp.name
                if len(basename) == 0:
                    logger.warning('create_filename:{0}'.format(os.path.basename(temp.name)))
                    basename = os.path.basename(temp_file_name) + self.getSuffix(r)
                p = Path(self.data, basename)
                i = 0;
                basePath = p
                while p.exists():
                    i += 1
                    p = p.with_name('{0}({1}){2}'.format(basePath.stem, i, basePath.suffix))
                    if sys.maxsize == i:
                        break
            
            os.replace(temp_file_name, str(p))
        if count == 0:
            logger.warning('input:{0} Empty'.format(self.file_list))
