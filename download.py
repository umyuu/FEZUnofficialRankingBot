# -*- coding: utf-8 -*-
from logging import getLogger
import os
import sys
from pathlib import Path
# library
import requests

logger = getLogger('__main__')

class download():
    def __init__(self, config):
        self.data = config['WORK_FOLDER']['UPLOAD']
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.file_list = config['DOWNLOAD']['FILE_LIST']
        self.file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
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
    def request(self):
        """
           internet -- (Get) --> local
           exists fileName
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
            r = requests.get(address, headers=headers)
            p = Path(self.data, os.path.basename(address))
            i = 0;
            basePath = p
            while p.exists():
                i += 1
                p = p.with_name('{0}({1}){2}'.format(basePath.stem, i, basePath.suffix))
                if sys.maxsize == i:
                    break
            with p.open('wb') as f:
                f.write(r.content)
        if count == 0:
            logger.warning('input:{0} Empty'.format(self.file_list))
