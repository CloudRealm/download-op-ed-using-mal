import gzip
import os
import bs4
import sys
import requests
import string
import argparse
import json

MALSETTINGS = {
    "site": "https://myanimelist.net/animelist/{0}"
}


def get_data_from_mal(user, format_slash=True, format_json=True):
    response = requests.get(MALSETTINGS["site"].format(user)).text
    soup = bs4.BeautifulSoup(response, "html.parser")
    data = soup.find('table', {"class": "list-table"})["data-items"]
    if format_slash:
        data = data.replace('\/', '/')

    if format_json:
        return json.loads(data)
    
    return data

def convert_priority(priority):
    return {
        "High":3,
        "Medium":2,
        "Low":1
    }[priority]

def website_filter_anime(
    animedata,
    minimum_score=0, minimum_priority=0,
    exclude_dropped=True, exclude_planned=True,
    excluded_anime=[]
):
    for anime in animedata:
        status = anime["status"]
        if (exclude_dropped and status == 4) or (exclude_planned and status == 6):
            continue

        score = anime["score"]
        if score < minimum_score:
            continue
        
        priority = convert_priority(anime["priority_string"])
        if priority < minimum_priority:
            continue

        malid = anime["anime_id"]
        name = anime["anime_title"]
        if name not in excluded_anime and malid not in excluded_anime:
            yield malid

def load_and_store_data(user,filename):
    with open(filename,'w') as file:
        file.write(get_data_from_mal(user,format_json=False))
    
    
    