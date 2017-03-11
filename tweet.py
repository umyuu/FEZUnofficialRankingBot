# -*- coding: utf-8 -*-
"""
    run script tweetbot.py
"""
import os
import sys
import platform
import subprocess
import shutil
# pylint: disable=C0103

class RestoreCD(object):
    """
        with statement.
        implements Restore　Current Diretory.
    """
    def __init__(self):
        self.__chdir = None
    @property
    def chdir(self):
        """
            @return chdir
        """
        return self.__chdir
    def __enter__(self):
        self.__chdir = os.getcwd()
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        os.chdir(self.__chdir)
class Alarm(object):
    """
        alarm event implements by Windows
    """
    def __init__(self, timeout):
        self.timeout = timeout
    def wait(self):
        """
            windows command timeout /T
        """
        if platform.system() == 'Windows':
            subprocess.call('timeout /T {0}'.format(self.timeout))
        return self

class Settings(object):
    """
        twitter.ini filecopy & edit confirm
    """
    def __init__(self):
        self.basedir = './resource'
        self.filename = 'twitter.ini'
        self.src = os.path.join(self.basedir, 'sample', self.filename)
        self.dst = os.path.join(self.basedir, 'auth', self.filename)
    def ischecksize(self):
        """
            twitter.ini sample file size 120.
        """
        return os.path.getsize(self.dst) >= 150
    def initialize(self):
        """
            copy & confirm
        """
        if not self.copy():
            return
        self.confirm()
    def copy(self):
        """
            sample file copy.
            exits file size check.
        """
        if not os.path.isfile(self.dst):
            shutil.copy(self.src, self.dst)
            return True
        if self.ischecksize():
            return False
        return True
    def confirm(self):
        """
            edit confirm.
        """
        message = 'Please edit\n file:{0}'.format(self.dst)
        print(message)
        while True:
            self.promptForString('(Y/N)>', 'Y')
            if not self.ischecksize():
                print(message)
                continue
            break
    def promptForString(self, prompt, keyCode):
        """
            @param {string}prompt   Message
                   {string}keyCode  confirmKey
            @return {string}keycode
        """
        while True:
            key = input(prompt).upper()
            if not key.startswith(keyCode):
                continue
            return key
if __name__ == "__main__":
    s = Settings()
    s.initialize()
    with RestoreCD():
        os.chdir(os.path.join(os.getcwd(), 'src'))
        Alarm(15).wait()
        try:
            ARGUMENT = ['python', 'tweetbot.py']
            ARGUMENT.extend(sys.argv[1:])
            subprocess.call(ARGUMENT)
        except KeyboardInterrupt as ex:
            print(ex)
        Alarm(60).wait()
