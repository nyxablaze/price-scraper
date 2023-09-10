import os
import platform
import requests
import json
import urllib.request as r
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse

def getdata(url):
    r = requests.get(url)
    return r.text

directory = os.getcwd()
architecture = platform.system()

#create empty dict
dict_href_links = {}

if architecture == "Windows":
    directory_path = (directory + r"\carsales-scraper")
elif architecture == ["Linux", "Darwin"]:
    directory_path = (directory + r"/carsales-scraper")
else:
    print("UNKNOWN OS, wtf bro")