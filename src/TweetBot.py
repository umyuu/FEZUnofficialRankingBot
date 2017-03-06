# -*- coding: utf-8 -*-
"""
    tweetbot main code.
"""
from logging import getLogger, StreamHandler, DEBUG
import argparse
from datetime import datetime
import os
import glob
#
import twitter
#
import serializer
import download
import country

# console output
logger = getLogger('myapp.tweetbot')
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class tweetbot(object):
    def __init__(self, config, args):
        self.args = args
        self.api = None
        self.__download = download.download(config)
        self.__country = country.country(config)
        self.uploadDir = config['WORK_DIRECTORY']['UPLOAD']
        self.backupDir = config['WORK_DIRECTORY']['BACKUP']
        self.dtnow = datetime.now()
        self.upload_file_suffixes = config['WORK_DIRECTORY']['SUFFIXES'].split('|')
        self.upload_max_file_size = config['UPLOAD']['MAX_FILESIZE']
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
        self.tweet_screen_name = config['TWEET']['SCREEN_NAME']
        self.tweet_limit = config['TWEET']['LIMIT']
        self.isTweet = True
        self.initialize()
    def initialize(self):
        """
            create working directory.
        """
        os.makedirs(self.uploadDir, exist_ok=True)
        os.makedirs(self.backupDir, exist_ok=True)
    @property
    def download(self):
        return self.__download
    @property
    def country(self):
        return self.__country
    def twitter_init(self):
        """
            twitter api constractor.
        """
        if self.api is None:
            self.api = twitter.Api(consumer_key=self.args['CONSUMER_KEY'],
                                   consumer_secret=self.args['CONSUMER_SECRET'],
                                   access_token_key=self.args['ACCESS_TOKEN'],
                                   access_token_secret=self.args['ACCESS_TOKEN_SECRET'])
    def getImage(self):
        """
            @yield media
        """
        for ext in self.upload_file_suffixes:
            for media in glob.iglob(os.path.join(self.uploadDir, ext)):
                # upload fileSize limit
                size = os.path.getsize(media)
                if size > self.upload_max_file_size:
                    logger.warning('skip:{0},size:{1},limit:{2}'.format(media, size, self.upload_max_file_size))
                    continue
                # Todo:check image file
                yield media
    def getFilePrefix(self, prefix='%Y%m%d%H%M_'):
        return self.dtnow.strftime(prefix)
    def tweet(self, media):
        """
            @params media uploadFile
        """
        try:
            ranking = self.country.getCountry(media)
            if ranking is None:
                logger.warning('OCR Error')
                return
            self.twitter_init()
            text = '{0}\n{1}\n'.format(self.getFilePrefix(self.tweet_datefmt), self.tweet_format)
            for i, contry in enumerate(ranking.ranking[:2], start=1):
                text += str(i) + '位:{name} {score} point\n'.format_map(contry)

            if self.isTweet:
                media_id = self.api.UploadMediaSimple(media=media)
                self.api.PostUpdate(status=text, media=media_id)
                logger.info('tweet')
            logger.info(text)
        except Exception as ex:
            logger.exception(ex)
    def deletetweet(self):
        """
            delete tweet
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
            newfile = os.path.join(self.backupDir, self.getFilePrefix() + os.path.basename(file))
            os.replace(file, newfile)
            logger.info('backup:{0}'.format(newfile))
        except Exception as ex:
            logger.exception(ex)


def main():
    """
        parse
    """
    parser = argparse.ArgumentParser(prog='tweetbot',
                                     description='FEZ Unofficial Total War Ranking TwitterBot')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.3')
    parser.add_argument('--debug', default=True)

    logger.info('Program START')
    args = parser.parse_args()
    
    #config = serializer.load_ini('../resource/setting.ini')
    config = serializer.load_json('../resource/setting.json')
    twitter_auth = serializer.load_ini(config['AUTH']['TWITTER'])
    #Set Twitter Apps Auth Keys
    twitter_auth_keys = dict()
    for key_name in ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']:
        twitter_auth_keys[key_name] = twitter_auth['AUTH'][key_name]

    bot = tweetbot(config, twitter_auth_keys)
    bot.isTweet = False
    bot.download.request()
    for media in bot.getImage():
        logger.info('tweet media:%s', media)
        bot.tweet(media)
        #bot.deletetweet()
        bot.backup(media)
    logger.info('Program END')

if __name__ == "__main__":
    main()
