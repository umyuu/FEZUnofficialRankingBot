# -*- coding: utf-8 -*-
import configparser
import pytest

from src import hsvcolor

class TestClass(object):
    def test_load(self):
        config = configparser.ConfigParser()
        with open('../resource/setting.ini', 'r', encoding='utf-8-sig') as f:
                config.read_file(f)
        c = hsvcolor.HSVcolor(0, 0, 0)
        assert c is not None

if __name__ == '__main__':
    pytest.main("--capture=sys")