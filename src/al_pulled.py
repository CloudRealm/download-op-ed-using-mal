import gzip
import os
import bs4
import sys
import requests
import string
import argparse
import json

ALSETTINGS = {
    "site":'https://graphql.anilist.co',
    "query":"""
query userList($user: String) {
  MediaListCollection(userName: $user, type: ANIME) {
    lists {
      status
        entries {
        score
        media {
          idMal
          title {
            romaji
          }
        }
      }
    }
  }
}
"""
}


def get_data_from_al(user):
    variables = {
	       "user":user
    }
    json_arg = {'query': ALSETTINGS["query"], 'variables': variables}
    response = requests.post(ALSETTINGS["site"], json=json_arg).json()
    if "errors" in response:
        raise Exception(f"[AL ERROR] {'; '.join(i['message'] for i in response['errors'])}\n{response['errors']}")
    data = response["data"]["MediaListCollection"]["lists"]
    
    return data
    
def convert_status(status):
    if type(status) is int:
        return status
    return {
        "CURRENT": 1,
        "COMPLETED": 2,
        "PAUSED": 3,
        "DROPPED": 4,
        None: 5,
        "PLANNING": 6,
    }[status]

def al_filter_anime(
    animedata,
    minimum_score=0,
    exclude_dropped=True, exclude_planned=True,
    excluded_anime=[]
):
    for medialist in animedata:
        status = convert_status(medialist["status"])
        if (exclude_dropped and status == 4) or (exclude_planned and status == 6):
            continue
    	       
        for entry in medialist["entries"]:
    	        score = entry["score"]
    	        if score < minimum_score:
    	            continue
    	            
    	        yield entry["media"]["idMal"]