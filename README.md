# FEZ Unofficial Ranking Bot [GitHub](https://github.com/umyuu/FEZUnofficialRankingBot)
FEZ 非公式な国家総力戦ランキングTwitterボット

ランキング画像をダウンロードして1位/2位の国名とポイントをツイート
## Install
1. [download a ZIP](https://github.com/umyuu/FEZUnofficialRankingBot/archive/master.zip) file.
2. Dependencies installs.
 1. [requirements install.](requirements.txt)

        `pip install -r requirements.txt`
 2. opencv3 install. 

         `conda install --channel https://conda.anaconda.org/menpo opencv3`
    
 3. Tesseract-OCR download & install.

        FileSize:**12.8 MB** [Windows Binary. version 3.20.2](https://sourceforge.net/projects/tesseract-ocr-alt/files/tesseract-ocr-setup-3.02.02.exe/download) 

        install download execute.

        FileSize:**42.3 MB** [Japanese language Model.](https://github.com/tesseract-ocr/tessdata/raw/master/jpn.traineddata) 

         download  Model file to install Tesseract-OCR Directory. Tesseract-OCR\tessdata\

         defalut Directory. C:\Program Files (x86)\Tesseract-OCR\tessdata

## Setup
1. Twitter Auth Settings.

    [Create New App Keys.](https://apps.twitter.com)

2. Python Run Script.

   `python tweet.py`

     1. resource\auth\twitter.ini Not Found.

        Please edit and save file with texteditor.

          `consumer_key, consumer_secret, access_token, access_token_secret`

## Dependencies
- python 3.5+
- python-twitter
- opencv
- numpy
- Pillow
- pyocr
- Tesseract-OCR

## Source code License
[MIT License](LICENSE)

## Links
- [Twitter bot](https://twitter.com/fez_ranking_bot)
- [開発環境](https://github.com/umyuu/FEZUnofficialRankingBot/wiki/%E9%96%8B%E7%99%BA%E7%92%B0%E5%A2%83)

## Copyright
【FEZ】 Fantasy Earth ZERO

© 2005-2017 SQUARE ENIX CO., Ltd. All Rights Reserved.
