# what's this project
This project allows you to automaticaly download opening and ending songs from all of your favorite anime without the need of downoading everything yourself. Since almost every weeb uses MAL to track the anime he's watching, this tool is really useful, as every information you need to give it has been written down already. All you need to do is to [export your anime list with this link](https://myanimelist.net/panel.php?go=export)  and place it in the same folder as the python file. You can just run it freely from console, if you want to change some settings, look at `python downloader.py -h`
# disclaimer
All videos are downloaded from animethemes.moe and originally belong to studios who made them. You are not allowed to distribute any videos downloaded, unless you have permission from the studios that made it and animethemes.moe.
Note that owning and distributing the program itself is allowed.
# how to use
- clone this repository or download all the required files
- do `pip install  -r requirements.txt` to install all required libraries
- import downloader.main or run in console
# arguments
```arg
usage: advanced.py [-h] [-f export] [-F folder] [--s [skip]] [-m min_score]
                   [--d [dropped]] [--p [planned]] [--a [audio]]
                   [--q [quality]] [-e excluded [excluded ...]]

Download anime openings and endings using a MAL export file and
animethemes.moe. By searching through your animelist and picking out every
anime, this program finds all of your liked anime. It then parses it and using
an animethemes.moe api finds all anime OP's and ED's. It then downloads it in
either mp3 or webm file format, allowing you to get that weeb shit you
deserve.

optional arguments:
  -h, --help            show this help message and exit
  -f export             MAL export file, can be zipped or unzipped.
  -F folder             Folder to save the integers into.
  --s [skip]            Skip songs that are already downloaded.
  -m min_score          Minimum score that has to be given to a show to be
                        downloaded.
  --d [dropped]         Include anime that has been dropped.
  --p [planned]         Include anime that hasn't been watched yet.
  --a [audio]           Download mp3 instead of video.
  --q [quality]         Download videos in higher quality.
  -e excluded [excluded ...]
                        All anime that should be excluded from download, can
                        be also MAL id.
```
# TODO
- smarter file recognition
- minor optimizations
- prettier printing
