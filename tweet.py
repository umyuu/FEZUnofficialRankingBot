# -*- coding: utf-8 -*-
"""
    run script tweetbot.py
"""
import os
import sys
import platform
import subprocess
import shutil

class RCD(object):
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
    def __init__(self):
        self.baseDir = './resource'
        self.filename = 'twitter.ini'
        self.src = os.path.join(self.baseDir, 'sample', self.filename)
        self.dst = os.path.join(self.baseDir, 'auth', self.filename)
    def isCheckSize(self):
        return os.path.getsize(self.dst) >= 150
    def initialize(self):
        if not self.copy():
            return
        self.confirm()
    def copy(self):
        if not os.path.isfile(self.dst):
            shutil.copy(self.src, self.dst)
            return True
        if self.isCheckSize():
            return False
        return True
    def confirm(self):
        message = 'Please edit\n file:{0}'.format(self.dst)
        print(message)
        while True:
            key = input('(Y/N)>').upper()
            if key != 'Y':
                continue
            if not self.isCheckSize():
                print(message)
                continue
            break

if __name__ == "__main__":
    s = Settings()
    s.initialize()
    with RCD():
        os.chdir(os.path.join(os.getcwd(), 'src'))
        Alarm(15).wait()
        try:
            ARGUMENT = ['python', 'tweetbot.py']
            ARGUMENT.extend(sys.argv[1:])
            subprocess.call(ARGUMENT)
        except KeyboardInterrupt as ex:
            print(ex)
        Alarm(60).wait()