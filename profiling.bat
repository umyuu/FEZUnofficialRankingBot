cd src
python -m cProfile -o ..\temp\program.prof TweetBot.py
snakeviz ..\temp\program.prof
TIMEOUT 30