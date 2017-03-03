#---------------------------------------------------
#	@fileoverview new issue script
#	creation date：2017/03/03
#	@license Copyright (c) 2017 うみゅ
#	This software is released under the MIT License.
#	http://opensource.org/licenses/mit-license.php
#---------------------------------------------------
from __future__ import unicode_literals, print_function
#
import argparse
from collections import OrderedDict
import os
import webbrowser
#
import platform
import cv2
import numpy as np
import PIL
import pyocr

class issue:
    def __init__(self):
        self.chrome_path = os.path.join(os.environ["ProgramFiles(x86)"], 'Google\Chrome\Application\chrome.exe')
        self.versions = OrderedDict()
        self.getDependencies()
    def getDependencies(self):
        self.versions['os'] = platform.system()
        self.versions['python'] = platform.python_version()
        self.versions['opencv'] = cv2.__version__
        self.versions['numpy'] = np.version.full_version
        self.versions['pillow'] = PIL.PILLOW_VERSION
        self.versions['pyocr'] = pyocr.VERSION
    def getVersionsText(self):
        return '<< ' + ', '.join([ '{0}={1}'.format(k, self.versions[k]) for k in self.versions.keys() ]) + ' >>'
    def toClipboard(self):
        params = 'echo "{0}" | clip.exe'.format(self.getVersionsText())
        os.system(params)
        return
    def open_webbrowser(self, url):
        browser = webbrowser.get('"{0}" %s'.format(self.chrome_path))
        browser.open_new_tab(url)
        return browser

def main():
    parser = argparse.ArgumentParser(description='new issue.')
    parser.add_argument('--user', '-u', default='umyuu',
                    help='using user')
    parser.add_argument('--repository', '-r', default='FEZUnofficialRankingBot',
                    help='using repository')
    args = parser.parse_args()

    me = issue()
    me.toClipboard()
    openurl = 'https://github.com/{0}/{1}/issues/new'.format(args.user, args.repository)
    me.open_webbrowser(openurl)
    
if __name__ == "__main__":
    main()
