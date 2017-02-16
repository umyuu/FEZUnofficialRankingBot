from logging import getLogger
from collections import OrderedDict
import os
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
        dic = OrderedDict()
        with open(self.file_list, 'r', encoding=self.file_list_encoding) as fin:
            for line in fin:
                text = line.rstrip('\n')
                if not text.startswith('http'):
                    logger.warning(text)
                    continue
                dic[text] = None
        if len(dic) == 0:
            logger.warning('input:{0} Empty '.format(self.file_list))
        return dic
    def request(self):
        # internet -> local
        dic = self.requestList()
        headers = {'User-Agent': self.user_agent}        
        for address in dic.keys():
            logger.info('download:{0}'.format(address))
            r = requests.get(address, headers=headers)
            #filepath = os.path.join(self.data, os.path.basename(address))
            
            #basepath = self.data
            #filepath = os.path.join(basepath, os.path.basename(address))
            # Randomize duplicate path
            #while not os.path.isfile(filepath):                
            #    filepath += 'a'
            #logger.info(filepath)                 
            #with open(filepath, 'wb') as fout:
            #    fout.write(r.content)
            with open(os.path.join(self.data, os.path.basename(address)), 'wb') as fout:
                fout.write(r.content)
