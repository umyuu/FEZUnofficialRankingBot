# pip install python-twitter
# https://apps.twitter.com
import configparser
from logging import getLogger, StreamHandler, DEBUG
import argparse
from collections import OrderedDict
from datetime import datetime
import os
import glob
import shutil
import requests
import twitter

config = configparser.ConfigParser()
with open('./setting.ini', 'r', encoding='utf-8') as f:
    config.read_file(f)
# console output
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class tweetbot():
    def __init__(self, args):
        self.args = args;
        self.t = None;
        self.upload = './upload/'
        self.images = './images/'
        self.dtNow = datetime.now()
        self.upload_file_size_limit = int(config['UPLOAD']['FILE_SIZE_LIMIT']);
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.download_file_list = config['DOWNLOAD']['FILE_LIST']
        self.download_file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
    def downloadImage(self):
        # internet -> local
        dic = OrderedDict()
        with open(self.download_file_list, 'r', encoding=self.download_file_list_encoding) as fin:
            for line in fin:
                text = line.rstrip('\n')
                if text.startswith('http'):
                    dic[text] = None 
                else:
                    logger.warning(text.encode(self.download_file_list_encoding))
                    continue
                    
        if len(dic.keys()) == 0:
            logger.warning('input:{0} Empty '.format(self.download_file_list))
            return
        headers = {'User-Agent': self.user_agent}        
        for address in dic.keys():
            logger.info('download:{0}'.format(address))
            r = requests.get(address, headers=headers)
            with open(os.path.join(self.upload, os.path.split(address)[1]), 'wb') as fout:
                fout.write(r.content)
    def getImage(self, files=None):
        if files is None:
            files = []
        for ext in ['*.png', '*.jpg']:
            for media in glob.iglob(os.path.join(self.upload, ext)):
                # upload fileSize limit
                size = os.path.getsize(media)
                if size < self.upload_file_size_limit:
                    files.append(media)
                else:
                    logger.warning('skip:{0}, size:{1}'.format(media, size))

        return files
    def getFilePrefix(self, prefix='%Y%m%d%H%M_'):
        return self.dtNow.strftime(prefix)
    def tweet(self, media):
        try:
            if self.t is None:
                self.t = twitter.Api(consumer_key=self.args.consumer_key,
                                     consumer_secret=self.args.consumer_secret,
                                     access_token_key=self.args.access_token,
                                     access_token_secret=self.args.access_token_secret)
            text = '{0}\n{1}'.format(self.getFilePrefix(self.tweet_datefmt), self.tweet_format)
            media_id = self.t.UploadMediaSimple(media=media)
            self.t.PostUpdate(status=text, media=media_id)
            logger.info(text)
        except Exception as ex:
            logger.exception(ex)
    def backup(self, file):
        # file change & move
        try:
            newFile = os.path.join(self.upload, self.getFilePrefix() + os.path.split(file)[1])
            os.rename(file, newFile)
            shutil.move(newFile, self.images)
        except Exception as ex:
            logger.exception(ex)

#if __name__ == "__main__":

# parse
parser = argparse.ArgumentParser(
    description='FEZ National Total War Ranking')
# must twitter auth params
parser.add_argument('--consumer_key', '-ck')
parser.add_argument('--consumer_secret', '-cs')
parser.add_argument('--access_token', '-at')
parser.add_argument('--access_token_secret', '-ats')

logger.info('')
bot = tweetbot(parser.parse_args())
bot.downloadImage()
for media in bot.getImage():
    logger.info('tweet media:{0}'.format(media))
    bot.tweet(media)
    bot.backup(media)
    #break

