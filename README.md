# FEZ Unofficial Ranking Bot [GitHub](https://github.com/umyuu/FEZUnofficialRankingBot)
FEZ 非公式な国家総力戦ランキングTwitterボット

## Install
[download a ZIP](https://github.com/umyuu/FEZUnofficialRankingBot/archive/master.zip) file.

## Setup
1. Dependencies installs.
 1. requirements install.

        `pip install -r requirements.txt`
 2. opencv install. 

         `conda install --channel https://conda.anaconda.org/menpo opencv3`
    
 3. Tesseract-OCR download & install.

        FileSize:**12.8 MB** [Windows Binary. version 3.20.2](https://sourceforge.net/projects/tesseract-ocr-alt/files/tesseract-ocr-setup-3.02.02.exe/download) 

        install download execute.

        FileSize:**42.3 MB** [Japanese language Model.](https://github.com/tesseract-ocr/tessdata/raw/master/jpn.traineddata) 

         download  Model file to install Tesseract-OCR Directory. Tesseract-OCR\tessdata\

         defalut Directory. C:\Program Files (x86)\Tesseract-OCR\tessdata

2. Twitter Apps Page Create App Keys.

    [Create New App](https://apps.twitter.com)

3. Python Run Script.

     `python TweetBot.py -ck [consumer_key] -cs [consumer_secret] -at [access_token] -ats [access_token_secret]`

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