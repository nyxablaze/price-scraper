import os
import platform
import requests
import json
import urllib.request as r
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
make = "honda"
model = "civic"
year = "2018"

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
    exit()

def get_links(website_link)
    html_data = getdata(website_link)
    soup = BeautifulSoup(html_data, 'html.parser')
    base_url = website_link.rstrip('/')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http'):
            parsed_uri = urlparse(href)
            if parsed_uri.netloc == 'www.carsales.com.au/' + make + "/" + model + "/price/" + year + "/":
                list_links.append(href)
            elif href.startswith('/'):
                full_link = urljoin(website_link, href)
                list_links.append(full_link)
            else:  
                pass
    list_links = [link for link in list_links if link.startswith('www.carsales.com.au' + make + model + "/price/")]
    dict_links = dict.fromkeys(list_links, 'Not-checked')
    return dict_links

def get_subpage_links(l):
    for link in tqdm(l):
        # If not crawled through this page start crawling and get links
        if l[link] == "Not-checked":
            dict_links_subpages = get_links(link)
            # Change the dictionary value of the link to "Checked"
            l[link] = "Checked"
        else:
            # Create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        # Add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}
    return l

website = "https://www.carsales.com.au/" + make + model + "/price/" + year + "/"
dict_links = {website: "Not-checked"}

counter, counter2 = None, 0
while counter != 0:
    counter2 += 1
    dict_links2 = get_subpage_links(dict_links)
    # Count the number of non-values and set counter to 0 if there are no values within the dictionary equal to the string "Not-checked"
    counter = sum(value == "Not-checked" for value in dict_links2.values())
    # Print some statements
    print("")
    print("THIS IS LOOP ITERATION NUMBER", counter2)
    print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
    print("NUMBER OF 'Not-checked' LINKS = ", counter)
    print("")
    dict_links = dict_links2
    # Save list in a JSON file
    with open("data.json", "w") as a_file:
        json.dump(dict_links, a_file)

filename = "data.json"
with open(filename, 'r') as fr:
    pre_ = fr.read()
    lines = pre_.split('\n')
    new_filename = filename.split('.')[0] + ".txt"  # To keep the same name except ext
    with open(new_filename, "a") as fw:
        fw.write("\n".join(lines))

urls = "data.txt"
with open(urls, 'r') as f:
    filedata = f.read()
    filedata = filedata.replace(': "Checked", ', ', ')
    filedata = filedata.replace('"', '')
    filedata = filedata.replace('{', '')
    filedata = filedata.replace(': Checked}', '')

with open(urls, 'w') as f:
    f.write(filedata)