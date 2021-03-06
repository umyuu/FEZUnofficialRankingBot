# -*- coding: utf-8 -*-
"""
    tweetbot main code.
"""
from logging import getLogger, StreamHandler, DEBUG
import logging.config
import argparse
from datetime import datetime
import os
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
#
import twitter
# pylint: disable=E0401
from serializer import Serializer
from fileutils import FileUtils
from events import SimpleEvent
import download
import ranking
# pylint: enable=E0401
# pylint: disable=C0103
# console output
logger = getLogger('myapp.tweetbot')
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(logging.Formatter('%(threadName)s:%(message)s'))
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
        self.event = SimpleEvent()
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
        self.task = OrderedDict()

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
            auth = Serializer.load_ini(self.auth_twitter)['AUTH']
            self.api = twitter.Api(consumer_key=auth['CONSUMER_KEY'],
                                   consumer_secret=auth['CONSUMER_SECRET'],
                                   access_token_key=auth['ACCESS_TOKEN'],
                                   access_token_secret=auth['ACCESS_TOKEN_SECRET'])
            auth = None

    def getImage(self):
        """
            @yield {string} media
        """
        #result = []
        for media in FileUtils.search(self.uploadDir, self.upload_file_suffixes):
            # upload fileSize limit
            size = os.path.getsize(media)
            if size > self.upload_max_file_size:
                logger.warning('skip:%s,size:%s,limit:%s', media, size, self.upload_max_file_size)
                self.backup(media)
                continue
            # Todo:check image file
            #result.append(media)
            yield media
        #return result

    def parallels(self):
        with self.get_Executor() as executor:
            future_to_media = {executor.submit(self.ranking.getResult, media): media for media in self.getImage()}
            for future in as_completed(future_to_media):
                media = future_to_media[future]
                try:
                    logger.info(media)
                    self.task[media] = future.result()
                except Exception as ex:
                    logger.exception(ex)

    def get_Executor(self, max_workers=4):
        return ThreadPoolExecutor(max_workers=max_workers)
        #return ProcessPoolExecutor(max_workers=max_workers)

    def tweet(self, media):
        """
            @param {string} media uploadFile
        """
        try:
            logger.info('tweet media:%s', media)
            ranks = self.task[media]
            if ranks is None:
                return
            self.twitter_init()
            text = self.dtnow.strftime(self.tweet_datefmt)
            self.fillspace = self.fillspace % 2 + 1
            text += ('{:<{fill}}').format('', fill=self.fillspace)
            text += '\n{0}\n'.format(self.tweet_format)
            for i, contry in enumerate(ranks.ranking[:2], start=1):
                text += str(i) + '位:{name} {point} point\n'.format_map(contry)
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
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.6')
    parser.add_argument('--debug', default=True)

    logger.info('START Program')
    parser.parse_args()

    config = Serializer.load_json('../resource/setting.json')
    bot = TweetBot(config)
    bot.event += bot.tweet
    bot.event += bot.backup
    bot.isTweet = False
    bot.download.request()
    bot.parallels()
    for media in bot.task.keys():
        bot.event(media)
        #bot.deletetweet()
    logger.info('END Program')

if __name__ == "__main__":
    main()
