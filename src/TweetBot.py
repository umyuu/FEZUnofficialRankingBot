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
# pylint: disable=E0401
import serializer
import download
import ranking
# pylint: enable=E0401
# pylint: disable=C0103
# console output
logger = getLogger('myapp.tweetbot')
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class TweetBot(object):
    """
        tweetbot main code.
    """
    def __init__(self, config):
        self.api = None
        self.dtnow = datetime.now()
        self.fillspace = 0
        self.isTweet = True
        self.auth_twitter = config['AUTH']['TWITTER']
        self.__download = download.Download(config)
        self.__ranking = ranking.Ranking(config)
        self.uploadDir = config['WORK_DIRECTORY']['UPLOAD']
        self.backupDir = config['WORK_DIRECTORY']['BACKUP']
        self.upload_file_suffixes = config['WORK_DIRECTORY']['SUFFIXES']
        self.upload_max_file_size = config['UPLOAD']['MAX_FILESIZE']
        node = config['TWEET']
        self.tweet_format = node['POST']['FORMAT']
        self.tweet_datefmt = node['POST']['DATEFMT']
        self.tweet_screen_name = node['SCREEN_NAME']
        self.tweet_limit = node['LIMIT']
        self.backup_file_prefix = config['BACKUP']['FILE']['PREFIX']
        self.initialize()
    def initialize(self):
        """
            create working directory.
        """
        os.makedirs(self.uploadDir, exist_ok=True)
        os.makedirs(self.backupDir, exist_ok=True)
    @property
    def download(self):
        """
            @return {Download}
        """
        return self.__download
    @property
    def ranking(self):
        """
            @return {Ranking}
        """
        return self.__ranking
    def twitter_init(self):
        """
            twitter api constractor.
        """
        if self.api is None:
            auth = serializer.load_ini(self.auth_twitter)['AUTH']
            self.api = twitter.Api(consumer_key=auth['CONSUMER_KEY'],
                                   consumer_secret=auth['CONSUMER_SECRET'],
                                   access_token_key=auth['ACCESS_TOKEN'],
                                   access_token_secret=auth['ACCESS_TOKEN_SECRET'])
            auth = None
    def getImage(self):
        """
            @yield {string} media
        """
        for ext in self.upload_file_suffixes:
            for media in glob.iglob(os.path.join(self.uploadDir, ext)):
                # upload fileSize limit
                size = os.path.getsize(media)
                if size > self.upload_max_file_size:
                    logger.warning('skip:%s,size:%s,limit:%s', media, size, self.upload_max_file_size)
                    self.backup(media)
                    continue
                # Todo:check image file
                yield media
    def tweet(self, media):
        """
            @param {string} media uploadFile
        """
        try:
            ranks = self.ranking.getResult(media)
            if ranks is None:
                return
            self.twitter_init()
            text = self.dtnow.strftime(self.tweet_datefmt)
            self.fillspace = self.fillspace % 2 + 1
            text += ('{:<{fill}}').format('', fill=self.fillspace)
            text += '\n{0}\n'.format(self.tweet_format)
            for i, contry in enumerate(ranks.ranking[:2], start=1):
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
                logger.info('delete:%s,posted:%s', s.text, s.created_at)
        except Exception as ex:
            logger.exception(ex)
    def backup(self, file):
        """
           moveTo
             src:@param {string} file
             dst:[images\YYYY-mm-dd_HHMM_]FileName.extensions
        """
        try:
            newfile = os.path.join(self.backupDir, self.dtnow.strftime(self.backup_file_prefix) + os.path.basename(file))
            os.replace(file, newfile)
            logger.info('backup:%s', newfile)
        except Exception as ex:
            logger.exception(ex)

def main():
    """
        1, FileDownload.
            i, ./DownloadList.txt contents HTTP GET to images/upload.
        2, TWEET.
            i, OCR. ranking#getResult
                images/upload Directory.
            ii, TWEET.
                api#PostUpdate
        3, Upload image to Backup.
            i, images/upload to images/backup
    """
    parser = argparse.ArgumentParser(prog='tweetbot',
                                     description='FEZ Unofficial Total War Ranking TwitterBot')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.4')
    parser.add_argument('--debug', default=True)

    logger.info('Program START')
    parser.parse_args()

    config = serializer.load_json('../resource/setting.json')
    bot = TweetBot(config)
    #bot.isTweet = False
    bot.download.request()
    for media in bot.getImage():
        logger.info('tweet media:%s', media)
        bot.tweet(media)
        #bot.deletetweet()
        bot.backup(media)
    logger.info('Program END')

if __name__ == "__main__":
    main()
