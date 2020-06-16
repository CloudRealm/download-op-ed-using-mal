from downloader import *
from requests import get
import re
from __future__ import unicode_literals
import gzip,os,bs4

API_OPED = ["OP","ED"]

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

def get_all_oped_names(animenames,shortened=False):
    output = []
    for i in animenames:
        if shortened:
            output += [i+" op",i+" ed"]
        else:
            output += [i+" opening",i+" ending"]
    return output
def filter_anime(animedata,minimum_score=0,exclude_dropped=True,exclude_planned=True,exclude_anime=[]):
    for anime in animedata:
        status = anime.find("my_status").text
        if ((exclude_dropped and status == "Dropped") or
             (exclude_planned and status == "Plan to Watch")):
                 continue
        score = int(anime.find("my_score").text)
        if score >= minimum_score:
            malid = anime.find("series_animedb_id").text
            name = anime.find("series_title").text
            if anime.find("series_title").text not in exclude_anime:
                yield [malid,name]


    
def download_anime(malid,name,folder=".",audio=False):
    if 1:
        site = 'https://animethemes-api.herokuapp.com/id/{0}/{1}'
        for op_ed in API_OPED:
            number = 1
            r = site.format(malid,op_ed)
            if audio:
                r += "audio/"
            r = get(r, allow_redirects=True)
            filename = f'{folder}/{name}({op_ed} {number})'
            with open(filename,'wb') as file:
                for chunk in r:
                    file.write(chunk)

def main(
export_file=None,
save_to_folder='.',
ignore_already_downloaded=False,
minimum_score=0,
exclude_dropped=True,exclude_planned=True,
exclude_anime=[],
download_audio=False,
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
    for malid,name in filter_anime(data,minimum_score,exclude_dropped,exclude_planned,exclude_anime):
        print("downloading",name)
        download_anime(malid,name,save_to_folder,download_audio)
        
if __name__ == '__main__':
    main(None,'bin')
            
            
            
