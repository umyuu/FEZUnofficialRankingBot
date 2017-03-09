# -*- coding: utf-8 -*-
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
#
import requests

# pylint: disable=C0103
def http_download(url, timeout):
    """
        @param {string}url
               {int}timeout
        @return {object}
    """
    execute_log = 'pid:{0},{1}'.format(os.getpid(), datetime.now().strftime('%F %T.%f'))
    res = requests.get(url, timeout=timeout)
    #raise Exception()
    return res.headers['content-type'], execute_log
def get_Executor():
    return ThreadPoolExecutor(max_workers=5)

def main():
    dtStart = datetime.now()
    baseURL = 'https://raw.githubusercontent.com/umyuu/FEZUnofficialRankingBot/'
    URLS = ['https://github.com/umyuu/GenshinCalculator/',
                   os.path.join(baseURL, 'master/resource/Casedria.png'),
                   os.path.join(baseURL, 'master/resource/Geburand.png'),
                   os.path.join(baseURL, 'master/resource/Hordine.png'),
                   os.path.join(baseURL, 'master/resource/Ielsord.png'),
                   os.path.join(baseURL, 'master/resource/Netzawar.png')
                   ]
    with get_Executor() as executor:
        future_to_url = {executor.submit(http_download, url, 60): url for url in URLS}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                print(future.result())
            except Exception as ex:
                print('%r http_download an exception: %s' % (url, ex))
    print('開始:{0}\n終了:{1}'.format(dtStart.strftime('%F %T.%f'),
          datetime.now().strftime('%F %T.%f')))

if __name__ == '__main__':
    main()
