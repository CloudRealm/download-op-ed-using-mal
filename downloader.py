from __future__ import unicode_literals
import gzip,os,bs4,sys,requests,string,argparse


APISETTINGS = {
    "oped":["OP","ED"],
    "site parse":"https://animethemes-api.herokuapp.com/id/{0}/",
    "site":"https://animethemes-api.herokuapp.com/id/{0}/{1}/",
    "audio":"audio/",
    "version priority":1
}

def make_printable(s):
    return ''.join(char for char in s if char in string.printable)



def search_for_export_file():
    for i in os.listdir():
        if i.startswith("animelist") and i.endswith(".xml.gz"):
            return i
    
def unpack_gzfile(filename):
    with gzip.open(filename,'r') as file:
        return file.read()
    
def open_unzipped_export_file():
    for i in os.listdir():
        if i.startswith("animelist") and i.endswith(".xml"):
            return i

def get_all_anime_data(xml_file):
    data = bs4.BeautifulSoup(xml_file,features="html.parser")
    return data.findAll("anime")

def filter_anime(
    animedata,
    minimum_score=0,
    exclude_dropped=True,exclude_planned=True,
    excluded_anime=[]
):
    for anime in animedata:
        status = anime.find("my_status").text
        if (exclude_dropped and status == "Dropped") or (exclude_planned and status == "Plan to Watch"):
            continue
             
        score = int(anime.find("my_score").text)
        if score < minimum_score:
            continue
        
        malid = anime.find("series_animedb_id").text
        name = anime.find("series_title").text
        if name not in excluded_anime and malid not in excluded_anime:
            yield malid
            

    
def api_parse(malid,download_HD=False,ignore_already_downloaded=False,folder='.'):
    already_downloaded = os.listdir(folder)
    
    site = APISETTINGS["site parse"].format(malid)
    data = requests.get(site).json()
    
    anime_name = data["name"]
    for song in data["themes"]:
        song_type = song["type"]
        if ' ' in song_type:
            song_type,version = song_type.split(' ');
            version = int(version[1:])
            if version != APISETTINGS["version priority"]:
                continue

        title = song["title"]
        
        mirror = song["mirror"]
        if len(mirror) > 1:
            mirror = mirror[download_HD]["mirrorUrl"]
        else:
            mirror = mirror[0]["mirrorUrl"]
        
        filename = f"{anime_name} {song_type} ({title}){' HD' if download_HD else ''}"
        filename += '.'+mirror.split('.')[-1]
        filename = make_printable(filename)
        
        if ignore_already_downloaded:
            if filename in already_downloaded:
                continue
        
        yield mirror,filename
        
def download_anime(site,filename,folder=".",audio=False):
    response = requests.get(site, allow_redirects=True)
    filename = f'{folder}/{filename}'
    
    with open(filename,'wb') as file:
        for chunk in response:
            file.write(chunk)

        
    
def main(
    export_file=None,
    folder='.',
    ignore_already_downloaded=False,
    minimum_score=0,
    exclude_dropped=True,exclude_planned=True,
    exclude_anime=[],
    download_audio=False,
    download_HD=False
):
    data = None
    if export_file is None:
        print("searching for an export file")
        export_file = search_for_export_file()
        if export_file is None:
            print("no export file found, searching for an unzipped export file")
            data = open_unzipped_export_file()
            if data is None:
                raise Exception("No export file found, make sure the export file looks like this: 'animelist_<date>.xml.gz'")
    
    if data is None:
        print("unpacking",export_file)
        data = unpack_gzfile(export_file)
    
    print("reading file")
    data = get_all_anime_data(data)
        
    print("getting anime names")
    for malid in filter_anime(data,minimum_score,exclude_dropped,exclude_planned,exclude_anime):
        print("[parse]",malid)
        for site,filename in api_parse(malid,download_HD,ignore_already_downloaded,folder):
            print("[download]",filename)
            download_anime(site,filename,folder,download_audio)
       
def get_parser():
    parser = argparse.ArgumentParser(description="""
Download anime openings and endings using a MAL export file and animethemes.moe.
By searching through your animelist and picking out every anime, this program finds all of your liked anime.
It then parses it and using an animethemes.moe api finds all anime OP's and ED's.
It then downloads it in either mp3 or webm file format, allowing you to get that weeb shit you deserve.
""")
    parser.add_argument('-f', metavar='export', type=str, default=None,
                        help='MAL export file, can be zipped or unzipped.')
    parser.add_argument('-F', metavar='folder', type=str, default='.',
                        help='Folder to save the integers into.')
    parser.add_argument('--s', metavar='skip', type=bool, default=False, const=True, nargs='?',
                        help='Skip songs that are already downloaded.')
    parser.add_argument('-m', metavar='min_score', type=int, default=0,
                        help='Minimum score that has to be given to a show to be downloaded.')
    parser.add_argument('--d', metavar='dropped', type=bool, default=True, const=False, nargs='?',
                        help='Include anime that has been dropped.')
    parser.add_argument('--p', metavar='planned', type=bool, default=True, const=False, nargs='?',
                        help='Include anime that hasn\'t been watched yet.')
    parser.add_argument('--a', metavar='audio', type=bool, default=True, const=False, nargs='?',
                        help='Download mp3 instead of video.')
    parser.add_argument('--q', metavar='quality', type=bool, default=False, const=True, nargs='?',
                        help='Download videos in higher quality.')
    parser.add_argument('-e', metavar='excluded', type=str, nargs='+', default=[],
                        help='All anime that should be excluded from download, can be also MAL id.')
    
    return parser

def convert_args(args):
    if args.a and args.q:
        raise ValueError("Cannot download HD audio files.")
    return {
        'export_file':args.f,
        'folder':args.F,
        'ignore_already_downloaded':args.s,
        'minimum_score':args.m,
        'exclude_dropped':args.d,
        'exclude_planned':args.p,
        'exclude_anime':args.e,
        'download_audio':args.a,
        'download_HD':args.q
    }
        
if __name__ == '__main__':
    
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    args = convert_args(args)
    main(**args)
