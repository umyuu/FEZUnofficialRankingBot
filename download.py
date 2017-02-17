# -*- coding: utf-8 -*-
from logging import getLogger
from collections import OrderedDict
import os
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
            @return yield  text
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
           internet -> local
           duplicate file 
             address[_SequentialNo]
        """
        count = 0
        headers = {'User-Agent': self.user_agent}
        for address in self.requestList():
            count += 1
        #for address in dic.keys():
            logger.info('download:{0}'.format(address))
            r = requests.get(address, headers=headers)
            #filepath = os.path.join(self.data, os.path.basename(address))
            
            #basepath = self.data
            #filepath = os.path.join(basepath, os.path.basename(address))
            # Randomize duplicate path
            #while not os.path.isfile(filepath):                
            #    filepath += 'a'
            #logger.info(filepath)
            p = Path(self.data, os.path.basename(address))
            i = 0;
            s = '_'
            while p.exists():
                old = p
                if not i == 0:
                    s = ''
                p =p.with_name('{0}{1}{2}{3}'.format(old.stem, s, str(i), old.suffix))
                i += 1
                logger.info("duplicate:")
                logger.info(p)
            
            with p.open('wb') as fout:
                fout.write(r.content)
            #with open(os.path.join(self.data, os.path.basename(address)), 'wb') as fout:
            #    fout.write(r.content)
        if count == 0:
            logger.warning('input:{0} Empty'.format(self.file_list))
