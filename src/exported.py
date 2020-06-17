import gzip
import os
import bs4
import sys
import requests
import string
import argparse
import json
from printer import *


def search_for_export_file():
    for i in os.listdir():
        if i.startswith("animelist") and i.endswith(".xml.gz"):
            return i


def open_export_file(export_file=None):
    data = None
    if export_file is None:
        fprint("read", f"searching for an export file")
        export_file = search_for_export_file()
        if export_file is None:
            fprint(
                "read", f"no export file found, searching for an unzipped export file")
            data = open_unzipped_export_file()
            if data is None:
                raise Exception(
                    "No export file found, make sure the export file looks like this: 'animelist_<date>.xml.gz'")

    if data is None:
        fprint("read", f"unpacking", export_file)
        data = unpack_gzfile(export_file)

    return data


def unpack_gzfile(filename):
    with gzip.open(filename, 'r') as file:
        return file.read()


def open_unzipped_export_file():
    for i in os.listdir():
        if i.startswith("animelist") and i.endswith(".xml"):
            with gzip.open(i, 'r') as file:
                return file.read()


def get_all_anime_data(xml_file):
    data = bs4.BeautifulSoup(xml_file, features="html.parser")
    return data.findAll("anime")


def convert_status(status):
    if type(status) is int:
        return status
    return {
        "Watching": 1,
        "Completed": 2,
        "On hold": 3,
        "Dropped": 4,
        None: 5,
        "Plan to Watch": 6,
        "All Anime": 7
    }


def filter_anime(
    animedata,
    minimum_score=0,
    exclude_dropped=True, exclude_planned=True,
    excluded_anime=[]
):
    for anime in animedata:
        status = anime.find("my_status").text
        status = convert_status(status)
        if (exclude_dropped and status == 4) or (exclude_planned and status == 6):
            continue

        score = int(anime.find("my_score").text)
        if score < minimum_score:
            continue

        malid = anime.find("series_animedb_id").text
        name = anime.find("series_title").text
        if name not in excluded_anime and malid not in excluded_anime:
            yield malid
