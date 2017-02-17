import configparser
from logging import getLogger, StreamHandler, DEBUG
import argparse
from datetime import datetime
import os
import glob
# library
import twitter
# app
import download
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
        self.api = None;
        self.download = download.download(config)
        self.upload = config['WORK_FOLDER']['UPLOAD']
        self.images = config['WORK_FOLDER']['images']
        self.dtNow = datetime.now()
        self.upload_max_file_size = int(config['UPLOAD']['MAX_FILESIZE']);
        self.tweet_format = config['TWEET']['FORMAT']
        self.tweet_datefmt = config['TWEET']['DATEFMT']
    def twitter_init(self):
        if self.api is None:
            self.api = twitter.Api(consumer_key=self.args.consumer_key,
                                 consumer_secret=self.args.consumer_secret,
                                 access_token_key=self.args.access_token,
                                 access_token_secret=self.args.access_token_secret)
    def downloadImage(self):
        # internet -> local
        self.download.request()
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
            self.twitter_init()
            text = '{0}\n{1}'.format(self.getFilePrefix(self.tweet_datefmt), self.tweet_format)
            #media_id = self.api.UploadMediaSimple(media=media)
            #self.api.PostUpdate(status=text, media=media_id)
            logger.info(text)
        except Exception as ex:
            logger.exception(ex)
    def deletetweet(self):
        """
            @params none
        """
        try:
            self.twitter_init()
            screen_name = 'fez_ranking_bot'
            limit = 1
            for s in self.api.GetUserTimeline(screen_name=screen_name, count=limit):
                self.api.DestroyStatus(s.id)
                logger.info('delete:{0},posted:{1}'.format(s.text, s.created_at))
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
parser.add_argument('--version', action='version', version='version 0.0.1')
parser.add_argument('--consumer_key', '-ck', required=True, help='Twitter Apps Auth set consumer_key')
parser.add_argument('--consumer_secret', '-cs', required=True, help='Twitter Apps Auth set consumer_secret')
parser.add_argument('--access_token', '-at', required=True, help='Twitter Apps Auth set access_token')
parser.add_argument('--access_token_secret', '-ats', required=True, help='Twitter Apps Auth set access_token_secret')
parser.add_argument('--debug', action='store_true', default=True)

logger.info('')
bot = tweetbot(parser.parse_args())
bot.downloadImage()
for media in bot.getImage():
    logger.info('tweet media:{0}'.format(media))
    bot.tweet(media)
    #bot.deletetweet()
    bot.backup(media)
    #break
