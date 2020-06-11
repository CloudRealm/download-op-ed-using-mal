# what's this project
This project allows you to automaticaly download opening and ending songs from all of your favorite anime without the need of downoading everything yourself. Since almost every weeb uses MAL to track the anime he's watching, this tool is really useful, as every information you need to give it has been written down already. All you need to do is to [export your anime list with this link](https://myanimelist.net/panel.php?go=export)  and place it in the same folder as the python file. You can just run it freely from console, but if you have some basic understanding of python, you can modify the settings.
# how to use
- clone this repository or download all the required files
- do `pip install  -r requirements.txt` to install all required libraries
- import downloader.py
- run downloader.main, add optional parameters

you can also run downloader.py in console, but you can't change any settings (for now)
# possible errors
- cannot download audio files
> you are most likely missing ffmpeg, try downloading it externaly
- files are  not downloading
> there's a possibility you are being rate limited, try waiting a while
# TODO
- higher usability in console
- downloading mp3 files without ffmpeg
- faster download speed
- smarter file recognition
- minor optimizations
- prettier printing
