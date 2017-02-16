import configparser
from logging import getLogger, StreamHandler, DEBUG
import argparse
from collections import OrderedDict
from datetime import datetime
import os
import glob
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
class download():
    def __init__(self, args):
        self.args = args;
        self.t = None;
        self.upload = config['WORK_FOLDER']['UPLOAD']
        self.images = config['WORK_FOLDER']['images']
        self.dtNow = datetime.now()
        self.upload_max_file_size = int(config['UPLOAD']['MAX_FILESIZE']);
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.download_file_list = config['DOWNLOAD']['FILE_LIST']
        self.download_file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
    def downloadList(self):
        dic = OrderedDict()
        with open(self.download_file_list, 'r', encoding=self.download_file_list_encoding) as fin:
            for line in fin:
                text = line.rstrip('\n')
                if not text.startswith('http'):
                    logger.warning(text)
                    continue
                dic[text] = None
        if len(dic) == 0:
            logger.warning('input:{0} Empty '.format(self.download_file_list))
        return dic
    def downloadImage(self):
        # internet -> local
        dic = self.downloadList()
        headers = {'User-Agent': self.user_agent}        
        for address in dic.keys():
            logger.info('download:{0}'.format(address))
            r = requests.get(address, headers=headers)
            filepath = os.path.join(self.upload, os.path.basename(address))
            
            #basepath = self.upload
            #filepath = os.path.join(basepath, os.path.basename(address))
            # Randomize duplicate path
            #while not os.path.isfile(filepath):                
            #    filepath += 'a'
            logger.info(filepath)                 
            #with open(filepath, 'wb') as fout:
            #    fout.write(r.content)
            with open(os.path.join(self.upload, os.path.basename(address)), 'wb') as fout:
                fout.write(r.content)
class tweetbot():
    def __init__(self, args):
        self.args = args;
        self.t = None;
        self.download = download(args)
        self.upload = config['WORK_FOLDER']['UPLOAD']
        self.images = config['WORK_FOLDER']['images']
        self.dtNow = datetime.now()
        self.upload_max_file_size = int(config['UPLOAD']['MAX_FILESIZE']);
        self.user_agent = config['DOWNLOAD']['USER_AGENT'];
        self.download_file_list = config['DOWNLOAD']['FILE_LIST']
        self.download_file_list_encoding = config['DOWNLOAD']['FILE_LIST_ENCODING']
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
    def downloadImage(self):
        # internet -> local
        self.download.downloadImage()
    def getImage(self, files=None):
        if files is None:
            files = []
        for ext in ['*.png', '*.jpg']:
            for media in glob.iglob(os.path.join(self.upload, ext)):
                # upload fileSize limit
                size = os.path.getsize(media)
                if size > self.upload_max_file_size:
                    logger.warning('skip:{0},size:{1},limit:{2},'.format(media, size, self.upload_max_file_size))
                    continue
                files.append(media)   

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
        # filename change & move
        try:
            newFile = os.path.join(self.images, self.getFilePrefix() + os.path.basename(file))
            os.replace(file, newFile)
            logger.info('backup:{0}'.format(newFile))
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

