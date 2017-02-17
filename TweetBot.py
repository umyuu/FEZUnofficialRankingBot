# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import configparser
import argparse
from datetime import datetime
import os
import glob
# library
import twitter
# Myapp library
import download

config = configparser.ConfigParser()
with open('./setting.ini', 'r', encoding='utf-8-sig') as f:
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
        self.api = None;
        self.download = download.download(config)
        self.upload = config['WORK_FOLDER']['UPLOAD']
        self.images = config['WORK_FOLDER']['images']
        self.dtNow = datetime.now()
        self.upload_file_suffixes = config['WORK_FOLDER']['SUFFIXES'].split('|')
        self.upload_max_file_size = int(config['UPLOAD']['MAX_FILESIZE'])
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
        self.tweet_screen_name = config['TWEET']['SCREEN_NAME']
        self.tweet_limit = int(config['TWEET']['LIMIT'])
    def twitter_init(self):
        if self.api is None:
            self.api = twitter.Api(consumer_key=self.args.consumer_key,
                                 consumer_secret=self.args.consumer_secret,
                                 access_token_key=self.args.access_token,
                                 access_token_secret=self.args.access_token_secret)
    def getImage(self):
        """
            @yield media
        """
        for ext in self.upload_file_suffixes:
            for media in glob.iglob(os.path.join(self.upload, ext)):
                # upload fileSize limit
                size = os.path.getsize(media)
                if size > self.upload_max_file_size:
                    logger.warning('skip:{0},size:{1},limit:{2}'.format(media, size, self.upload_max_file_size))
                    continue
                yield media
    def getFilePrefix(self, prefix='%Y%m%d%H%M_'):
        return self.dtNow.strftime(prefix)
    def tweet(self, media):
        """
            @params media uploadFile
        """
        try:
            self.twitter_init()
            text = '{0}\n{1}'.format(self.getFilePrefix(self.tweet_datefmt), self.tweet_format)
            isTweet = False
            isTweet = True
            if isTweet:
                media_id = self.api.UploadMediaSimple(media=media)
                self.api.PostUpdate(status=text, media=media_id)
            logger.info(text)
        except Exception as ex:
            logger.exception(ex)
    def deletetweet(self):
        """
            
        """
        try:
            self.twitter_init()
            for s in self.api.GetUserTimeline(screen_name=self.tweet_screen_name, count=self.tweet_limit):
                self.api.DestroyStatus(s.id)
                logger.info('delete:{0},posted:{1}'.format(s.text, s.created_at))
        except Exception as ex:
            logger.exception(ex)
    def backup(self, file):
        """
           moveTo
             src:@params file
             dst:[images\YYYYmmddHHMM_]FileName.extensions
        """
        try:
            newFile = os.path.join(self.images, self.getFilePrefix() + os.path.basename(file))
            os.replace(file, newFile)
            logger.info('backup:{0}'.format(newFile))
        except Exception as ex:
            logger.exception(ex)

#if __name__ == "__main__":
"""
  parse
    must twitter auth params
"""
parser = argparse.ArgumentParser(prog='tweetbot',
    description='FEZ Unofficial National Total War Ranking TwitterBot')
parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
parser.add_argument('--consumer_key', '-ck', required=True, help='Twitter Apps Auth set consumer_key')
parser.add_argument('--consumer_secret', '-cs', required=True, help='Twitter Apps Auth set consumer_secret')
parser.add_argument('--access_token', '-at', required=True, help='Twitter Apps Auth set access_token')
parser.add_argument('--access_token_secret', '-ats', required=True, help='Twitter Apps Auth set access_token_secret')
parser.add_argument('--debug', action='store_true', default=True)

logger.info('START')
bot = tweetbot(parser.parse_args())
bot.download.request()
for media in bot.getImage():
    logger.info('tweet media:{0}'.format(media))
    bot.tweet(media)
    #bot.deletetweet()
    bot.backup(media)
logger.info('END')
