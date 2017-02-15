# pip install python-twitter
# https://apps.twitter.com
import argparse
from datetime import datetime
import os
import glob
import shutil
import requests

class tweetbot():
    def __init__(self, args):
        self.args = args;
        self.t = None;
        self.upload = './upload/'
        self.images = './images/'
        self.dtNow = datetime.now()
        self.upload_file_limit = args.upload_file_limit;
        self.user_agent = args.user_agent;
    def downloadImage(self, address):
        headers = {'User-Agent': self.user_agent}
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
                if size < self.upload_file_limit:
                    files.append(media)
                else:
                    print('skip:{0}, size:{1}'.format(media, size))

        return files
    def getFilePrefix(self, prefix='%Y%m%d%H%M_'):
        return self.dtNow.strftime(prefix)
    def tweet(self, media):
        import twitter
        if self.t is None:
            self.t = twitter.Api(consumer_key=self.args.consumer_key,
                                 consumer_secret=self.args.consumer_secret,
                                 access_token_key=self.args.access_token,
                                 access_token_secret=self.args.access_token_secret)
        text = '{0}\nFEZ 国家総力戦ランキング'.format(self.getFilePrefix('%Y/%m/%d %H:%M'))
        media_id = self.t.UploadMediaSimple(media=media)
        self.t.PostUpdate(status=text, media=media_id)

    def backup(self, file):
        # file change & move
        try:
            newFile = os.path.join(self.upload, self.getFilePrefix() + os.path.split(file)[1])
            os.rename(file, newFile)
            shutil.move(newFile, self.images)
        except Exception as ex:
            print(ex)

# parse
parser = argparse.ArgumentParser(
    description='FEZ National Total War Ranking')
# twitter auth params
parser.add_argument('--consumer_key', '-ck')
parser.add_argument('--consumer_secret', '-cs')
parser.add_argument('--access_token', '-at')
parser.add_argument('--access_token_secret', '-ats')
# optional
parser.add_argument('--user_agent', '-ua', default='Mozilla/5.0 (compatible; bot/0.1; +https://twitter.com/fez_ranking_bot)')
parser.add_argument('--upload_file_limit', '-limit', type=int, default=104448)

print('')
bot = tweetbot(parser.parse_args())
bot.downloadImage('https://i.gyazo.com/919c7be6531ffeb5cfeb1e6e701556d3.png')
for media in bot.getImage():
    print('tweet media:{0}'.format(media))
    bot.tweet(media)
    bot.backup(media)
    #break
