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
import country

# console output
logger = getLogger('myapp.tweetbot')
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
def loadConfig(path, encoding='utf-8-sig'):
    c = configparser.ConfigParser()
    with open(path, 'r', encoding=encoding) as f:
        c.read_file(f)
    return c

config = loadConfig('../setting.ini')
twitter_auth = None
try:
    twitter_auth = loadConfig('../twitter_auth.ini')
    auth_params = ['CONSUMER_KEY','CONSUMER_SECRET','ACCESS_TOKEN','ACCESS_TOKEN_SECRET']
    for p in auth_params:
        if len(twitter_auth['AUTH'][p]) == 0:
            twitter_auth = None
            break
except (FileNotFoundError):
    pass

class tweetbot(object):
    def __init__(self, args):
        self.args = args;
        self.api = None;
        self.__download = download.download(config)
        self.__country = country.country(config)
        self.upload = config['WORK_FOLDER']['UPLOAD']
        self.images = config['WORK_FOLDER']['images']
        self.dtNow = datetime.now()
        self.upload_file_suffixes = config['WORK_FOLDER']['SUFFIXES'].split('|')
        self.upload_max_file_size = int(config['UPLOAD']['MAX_FILESIZE'])
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
        self.tweet_screen_name = config['TWEET']['SCREEN_NAME']
        self.tweet_limit = int(config['TWEET']['LIMIT'])
    @property
    def download(self):
        return self.__download
    @property
    def country(self):
        return self.__country
    def twitter_init(self):
        if self.api is None:
            self.api = twitter.Api(consumer_key=self.args['consumer_key'],
                                 consumer_secret=self.args['consumer_secret'],
                                 access_token_key=self.args['access_token'],
                                 access_token_secret=self.args['access_token_secret'])
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
                # Todo:check image file
                yield media
    def getFilePrefix(self, prefix='%Y%m%d%H%M_'):
        return self.dtNow.strftime(prefix)
    def tweet(self, media):
        """
            @params media uploadFile
        """
        try:
            ranks = self.country.getCountry(media)
            if ranks is None:
                logger.warning('OCR Error')
                return
            self.twitter_init()
            text = '{0}\n{1}\n'.format(self.getFilePrefix(self.tweet_datefmt), self.tweet_format)
            for i, contry in enumerate([ranks.rank1, ranks.rank2], start=1):
                text += str(i) + '位:{name} {score} point\n'.format_map(contry)
            
            isTweet = False
            isTweet = True
            if isTweet:
                media_id = self.api.UploadMediaSimple(media=media)
                self.api.PostUpdate(status=text, media=media_id)
                logger.info('tweet')
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


def main():
    """
        parse
            must twitter auth params
    """
    parser = argparse.ArgumentParser(prog='tweetbot',
                                     description='FEZ Unofficial Total War Ranking TwitterBot')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('--consumer_key', '-ck', help='Twitter Apps Auth set consumer_key')
    parser.add_argument('--consumer_secret', '-cs', help='Twitter Apps Auth set consumer_secret')
    parser.add_argument('--access_token', '-at', help='Twitter Apps Auth set access_token')
    parser.add_argument('--access_token_secret', '-ats', help='Twitter Apps Auth set access_token_secret')
    parser.add_argument('--debug', default=True)
    
    logger.info('START')
    args = parser.parse_args()
    
    dic_auth = dict()
    dic_auth['consumer_key'] = args.consumer_key
    dic_auth['consumer_secret'] = args.consumer_secret
    dic_auth['access_token'] = args.access_token 
    dic_auth['access_token_secret'] = args.access_token_secret
    if twitter_auth is not None:
        dic_auth['consumer_key'] = twitter_auth['AUTH']['CONSUMER_KEY']
        dic_auth['consumer_secret'] = twitter_auth['AUTH']['CONSUMER_SECRET']
        dic_auth['access_token'] = twitter_auth['AUTH']['ACCESS_TOKEN']
        dic_auth['access_token_secret'] = twitter_auth['AUTH']['ACCESS_TOKEN_SECRET']
     
    bot = tweetbot(dic_auth)
    bot.download.request()
    for media in bot.getImage():
        logger.info('tweet media:{0}'.format(media))
        bot.tweet(media)
        #bot.deletetweet()
        bot.backup(media)
        logger.info('END')
    
if __name__ == "__main__":
    main()