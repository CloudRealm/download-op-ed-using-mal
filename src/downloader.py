from __future__ import unicode_literals
import gzip
import os
import bs4
import sys
import requests
import string
import argparse
import json
import platform
from mal_pulled import *
from mal_exported import *
from printer import *
from al_pulled import *

APISETTINGS = {
    "oped": ["OP", "ED"],
    "site parse": "https://animethemes-api.herokuapp.com/id/{0}/",
    "audio site": "https://animethemes-api.herokuapp.com/id/{0}/{1}/audio",
    "filetypes": {"audio": ".mp3", "video": ".webm"}
} 

system = platform.system()
if system == "Darwin": system = "Mac"

BANNED_CHARS = {
    "Linux":"/",
    "Windows":'<>:"/\\|?*',
    "Mac":":"
}[system]


def api_check_errors(malid):

    site = APISETTINGS["site parse"].format(malid)
    try:
        data = requests.get(site).json()
    except:
        fprint("Error", f"API error: {malid} does bot have an entry in {site}")
        return

    if "name" not in data:
        fprint("Error", f"API error: {malid} has an empty entry in {site}")
        return

    return data


def api_parse(malid, download_HD=False, download_audio=False, ignore_already_downloaded=False, 
              preferred_version=1, folder='.', banned_chars='/', only_ascii=False, max_file_lenght=-1):
    data = api_check_errors(malid)
    if data is None:
        return []

    try:
        os.mkdir(folder)
    except:
        pass
    already_downloaded = os.listdir(folder)

    fprint("parse", malid)

    anime_name = data["name"]
    for song in data["themes"]:
        song_type_version = song["type"]
        if ' ' in song_type_version:
            song_type, version = song_type_version.split(' ')
            version = int(version[1:])
            if version != preferred_version:
                continue
        else:
            song_type = song_type_version

        title = song["title"]
        video_is_hd = False
        if download_audio:
            mirror = APISETTINGS["audio site"].format(malid, song_type_version)
            filetype = APISETTINGS["filetypes"]["audio"]
        else:
            mirror = song["mirror"]
            if len(mirror) > 1:
                mirror = mirror[download_HD]["mirrorUrl"]
                video_is_hd = download_HD
            else:
                mirror = mirror[0]["mirrorUrl"]
            filetype = APISETTINGS["filetypes"]["video"]


        filename = f"{anime_name} {song_type} ({title}){' HD' if video_is_hd else ''}"
        
        if only_ascii:
            filename = ''.join(char for char in filename if char in string.printable)
        filename = ''.join(char for char in filename if char not in BANNED_CHARS)
            
        if max_file_lenght > 0:
            filename = filename[:max_file_lenght]
        
        filename += filetype

        if ignore_already_downloaded:
            if filename in already_downloaded:
                continue

        yield mirror, filename


def download_anime(site, filename, folder="."):
    try:
        response = requests.get(site, allow_redirects=True)
    except:
        return f"No file found at {site}"
    if response.status_code != 200:
        return f"{response.status_code} in {site}"
    filename = f'{folder}/{filename}'
    
    with open(filename, 'wb') as file:
        for chunk in response:
            file.write(chunk)
    return False


def main(
    export_file=None,
    mal_username=None,al_username=None,
    folder='.',
    ignore_already_downloaded=False,
    minimum_score=0,minimum_priority=0,
    exclude_dropped=True, exclude_planned=True,
    exclude_anime=[],
    download_audio=False,
    download_HD=False,
    banned_chars='/',only_ascii=False,
    preferred_version=1,
    max_file_lenght=-1
):
    fprint("start","Launching program")
    if mal_username is not None:
        fprint("read", f"reading anime list of {mal_username} (MAL)")
        data = get_data_from_mal(mal_username)

        fprint("read", f"getting anime names")
        for malid in mal_filter_anime(data, minimum_score, minimum_priority, exclude_dropped, exclude_planned, exclude_anime):

            for site, filename in api_parse(malid, download_HD, download_audio, ignore_already_downloaded, preferred_version, folder, banned_chars, only_ascii, max_file_lenght):

                fprint("download", filename)
                response = download_anime(site, filename, folder)
                if response:
                    fprint("Error", f"connection/API error: {response}") 
                    
    elif al_username is not None:
        fprint("read", f"reading anime list of {mal_username} (AniList)")
        data = get_data_from_al(al_username)

        fprint("read", f"getting anime names")
        for malid in al_filter_anime(data, minimum_score, exclude_dropped, exclude_planned, exclude_anime):

            for site, filename in api_parse(malid, download_HD, download_audio, ignore_already_downloaded, preferred_version, folder, banned_chars, only_ascii, max_file_lenght):

                fprint("download", filename)
                response = download_anime(site, filename, folder)
                if response:
                    fprint("Error", f"connection/API error: {response}") 
                    
    
    else:
        data = open_export_file(export_file)

        fprint("read", f"reading file")
        data = get_all_export_data(data)

        fprint("read", f"getting anime names")
        for malid in mal_export_filter_anime(data, minimum_score, exclude_dropped, exclude_planned, exclude_anime):

            for site, filename in api_parse(
                malid, download_HD, download_audio, ignore_already_downloaded, 
                preferred_version, folder, banned_chars, only_ascii):

                fprint("download", filename)
                response = download_anime(site, filename, folder)
                if response:
                    fprint("Error", f"connection/API error: {response}")


 
def get_parser():
    
    parser = argparse.ArgumentParser(description="""
Download anime openings and endings using your AML username or a MAL export file and animethemes.moe.
By searching through your animelist and picking out every anime, this program finds all of your liked anime.
It then parses it and using an animethemes.moe api finds all anime OP's and ED's.
It then downloads it in either mp3 or webm file format, allowing you to get that weeb shit you deserve.
""")
    parser.add_argument('-f', metavar='export', type=str, default=None,
                        help='MAL export file, can be zipped or unzipped.')
    parser.add_argument('-mal', metavar='mal_username', type=str, default=None,
                        help='MAL username, used to pull data from MAL')
    parser.add_argument('-al', metavar='al_username', type=str, default=None,
                        help='AniList username, used to pull data from AniList')
    parser.add_argument('-F', metavar='folder', type=str, default='.',
                        help='Folder to save the songs into.')
    parser.add_argument('--s', metavar='skip', type=bool, default=False, const=True, nargs='?',
                        help='Skip songs that are already downloaded.')
    
    parser.add_argument('-m', metavar='min_score', type=int, default=0,
                        help='Minimum score that has to be given to a show to be downloaded.')
    parser.add_argument('-pr', metavar='min_priority', type=int, default=0,
                        help='Minimum priority that has to be given to a show to be downloaded, only with MAL. (Low=1,Normal=2,High=3)')
    
    parser.add_argument('--d', metavar='dropped', type=bool, default=True, const=False, nargs='?',
                        help='Include anime that has been dropped')
    parser.add_argument('--p', metavar='planned', type=bool, default=True, const=False, nargs='?',
                        help="Inclu de anime that hasn't been watched yet.")
    
    parser.add_argument('--a', metavar='audio', type=bool, default=False, const=True, nargs='?',
                        help='Download mp3 instead of video.')
    parser.add_argument('--q', metavar='quality', type=bool, default=False, const=True, nargs='?',
                        help='Download videos in higher quality.')
    
    parser.add_argument('-v', metavar='preferred_version', type=int, default=1,
                        help='Preferred version to download, used to download openings that otherwise cause problems')
    parser.add_argument('-e', metavar='excluded', type=str, nargs='+', default=[],
                        help='All anime that should be excluded from download, can be also MAL id.')
    
    parser.add_argument('-bc', metavar='banned_chars', type=str, default=BANNED_CHARS,
                        help=f'All banned characters, defaults to {BANNED_CHARS}, because you are currently using a {system} os')
    parser.add_argument('--ascii', metavar='only_ascii_chars', type=bool, default=False, const=True, nargs='?',
                        help='Creates files with only ascii characters in the name.')
    parser.add_argument('-ml', metavar='max_file_lenght', type=int, default=-1,
                        help='Limits the lenght of a file (excluding the extension), mostly good for Mac.')

    return parser


def convert_args(args):
    
    if args.a and args.q:
        raise ValueError("Cannot download HD audio files.")
    
    elif args.mal:
        if args.f:
            raise ValueError("Cannot search myanimelist.net and read a file at the same time.")
        elif args.al:
            raise ValueError("Cannot search MAL and read and export file at the same time")
    elif args.pr:
        if args.f:
            raise ValueError("Cannot check priority with an exported anime list.")
        else:
            raise ValueError("Cannot check priority without a MAL username.")
        
    return {
        'export_file': args.f,
        'mal_username': args.mal,
        'al_username':args.al,
        'folder': args.F,
        'ignore_already_downloaded': args.s,
        'minimum_score': args.m,
        'minimum_priority':args.pr,
        'exclude_dropped': args.d,
        'exclude_planned': args.p,
        'exclude_anime': args.e,
        'download_audio': args.a,
        'download_HD': args.q,
        'banned_chars':args.bc,
        'only_ascii':args.ascii,
        'preferred_version': args.v,
        'max_file_lenght': args.ml
    }


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    args = convert_args(args)
    main(**args)
