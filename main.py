"""
requirement:
    python 3.4+
packages:
    bs4
    youtube_dl (youtube-dl)
    youtube_search (youtube-search)
"""
from __future__ import unicode_literals
import gzip,os,bs4,youtube_dl
from youtube_search import YoutubeSearch
from pprint import pprint

def search_for_export_file():
    for i in os.listdir():
        if i.startswith("animelist") and i.endswith(".xml.gz"):
            return i
def unpack_gzfile(filename):
    with gzip.open(filename,'r') as file:
        return file.read()

def get_all_anime_data(xml_file):
    data = bs4.BeautifulSoup(xml_file,features="html.parser")
    return data.findAll("anime")

def get_anime_names(animedata,minimum_score=0,exclude_dropped=True,exclude_planned=True,exclude_anime=[]):
    for anime in animedata:
        status = anime.find("my_status").text
        if ((exclude_dropped and status == "Dropped") or
             (exclude_planned and status == "Plan to Watch")):
                 continue
        score = int(anime.find("my_score").text)
        if score >= minimum_score:
            name = anime.find("series_title").text
            if name not in exclude_anime:
                yield name

def get_all_oped_names(animenames,shortened=False):
    output = []
    for i in animenames:
        if shortened:
            output += [i+" op",i+" ed"]
        else:
            output += [i+" opening",i+" ending"]
    return output

def search_for_videolinks(videonames,rejected_ids=[],max_searched=10):
    for video in videonames:
        results = []
        while not results:
            results = YoutubeSearch(video,max_results=max_searched).to_dict()
        for result in results:
            if result["id"][:11] not in rejected_ids:
                rejected_ids += result["id"]
                yield result
                break

def download_from_youtube(link,filename,folder='.',ydl_opts={}):
    ydl_opts["outtmpl"] = folder+'/'+filename+".%(ext)s"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def main(
export_file=None,
save_to_folder='.',
ignore_already_downloaded=True,
minimum_score=0,
exclude_dropped=True,exclude_planned=True,
exclude_anime=[],
use_abbreviation=False,
rejected_yt_ds=[],max_yt_searched=10,
ydl_opts={}
):
    if export_file is None:
        print("searching for an export file")
        export_file = search_for_export_file()
        
    print("unpacking",export_file)
    data = unpack_gzfile(export_file)
    
    print("reading file")
    data = get_all_anime_data(data)
    
    if ignore_already_downloaded:
        print("excluding already downloaded songs")
        exclude_anime += [' '.join(i.split()[:-1]) for i in os.listdir(save_to_folder)]
        
    print("getting anime names")
    data = get_anime_names(data,minimum_score,exclude_dropped,exclude_planned,exclude_anime)
    
    data = get_all_oped_names(data,use_abbreviation)
    print("searching anime songs\n")
    
    search_results = search_for_videolinks(data,rejected_yt_ds,max_yt_searched)
    for name,i in zip(data,search_results):
        print("found",i["title"],"with id:",i["id"])
        
        link = 'http://www.youtube.com'+i["link"]
        try:
            download_from_youtube(link,name,save_to_folder,ydl_opts)
        except youtube_dl.utils.DownloadError as e:
            print(e)
            print("To solve this error, change your internet connection or try again in a few minutes.")
            

if __name__ == '__main__':
    main(None,'bin')