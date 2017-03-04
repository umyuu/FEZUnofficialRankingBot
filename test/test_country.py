# -*- coding: utf-8 -*-
import pytest

from src import TweetBot

class TestClass(object):
    def test_loadSettingFile(self):
        config = TweetBot.loadConfig('../resource/setting.ini')
        twitter_auth = TweetBot.loadConfig(config['AUTH']['TWITTER'])

if __name__ == '__main__':
    pytest.main("--capture=sys")