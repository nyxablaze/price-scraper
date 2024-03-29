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
variant = 'vti-l'
bodytype = 'hatch'

if bodytype == 'hatchback':
    bodytype == 'hatch'

if variant == '':
    variant = "no-badge"

def check_bodytype(html_content, bodytype):
    soup = BeautifulSoup(html_content, 'html.parser')
    bodytype_element = soup.find('i', class_='icon-body-type')
    
    if bodytype_element:
        # Find the <p> tag containing the bodytype information
        p_element = bodytype_element.find_next('p')
        if p_element and p_element.text.strip().lower() == bodytype.lower():
            return True
    return False

def getdata(url):
    r = requests.get(url)
    return r.text

directory = os.getcwd()
architecture = platform.system()

#create empty dict
dict_href_links = {}

if architecture == "Windows":
    directory_path = (directory + r"\carsales-scraper\\")
elif architecture in ["Linux", "Darwin"]:
    directory_path = (directory + r"/carsales-scraper/")
else:
    print("UNKNOWN OS, wtf bro")
    exit()

def get_links(website_link):
    html_data = getdata(website_link)
    soup = BeautifulSoup(html_data, 'html.parser')
    base_url = website_link.rstrip('/')

    # Initialize list_links as an empty list
    list_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http'):
            parsed_uri = urlparse(href)
            if parsed_uri.netloc == 'www.carsales.com.au' + make + '/' + model + '/price/' + year + '/' + variant + '-':
                list_links.append(href)
        elif href.startswith('/'):
            full_link = urljoin(website_link, href)
            list_links.append(full_link)
        else:
            pass
    list_links = [link for link in list_links if link.startswith('https://www.carsales.com.au/' + make + '/' + model + '/price/' + year + '/' + variant + '-')]
    dict_links = dict.fromkeys(list_links, "Not-checked")
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

website = 'https://www.carsales.com.au/' + make + '/' + model + '/price/' + year + '/'
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

# Save the desired links with variable numbers to data.txt
with open("data.txt", "w") as data_file:
    for link in dict_links.keys():
        data_file.write(link + '\n')

filename = "data.json"
with open(filename, 'r') as fr:
    pre_ = fr.read()
    lines = pre_.split('\n')
    new_filename = filename.split('.')[0] + ".txt"  # To keep the same name except ext
    with open(new_filename, "a") as fw:
        fw.write("\n".join(lines))

with open("data.txt", "w") as data_file:
    for link in dict_links.keys():
        data_file.write(link + ',\n')  # Add a comma and newline to separate the URLs

urls = "data.txt"
with open(urls, 'r') as f:
    filedata = f.read()
    filedata = filedata.replace(': "Checked", ', ', ')
    filedata = filedata.replace('"', '')
    filedata = filedata.replace('{', '')
    filedata = filedata.replace(': Checked}', '')

with open(urls, 'w') as f:
    f.write(filedata)

# scraper

urls2 = open('data.txt', 'r', encoding='utf-8-sig', errors='ignore')
data = urls2.read()
data_to_list = data.replace('\n', ' ').split(', ')
option = 0

# Initialize a variable to keep track of whether a matching body type is found
matching_body_type_found = False
price_when_new = None
private_price_guide = None
image_url = None

# Loop through the URLs
for url in data_to_list:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"HTTP Error {response.status_code}: An error occurred for {url}")
        else:
            option = option + 1
            optionstring = str(option)
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.title
            if title_tag and title_tag.string:
                htmltitle = title_tag.string
                print(url)
                title = "".join(x for x in htmltitle if x.isalnum())
                page = r.urlopen(url)
                html_content = page.read().decode('utf-8-sig')

                # Check if the HTML file contains the bodytype information
                if check_bodytype(html_content, bodytype):
                    print(f"HTML file {optionstring} contains the bodytype: {bodytype}")
                    matching_body_type_found = True

                    # Extract price data
                    price_when_new_element = soup.find('div', class_='items').find('p', class_='label', string='Price when new (EGC) ^')
                    if price_when_new_element:
                        price_when_new = price_when_new_element.find_next('p', class_='highlight-text').text.strip()

                    private_price_guide_element = soup.find('div', class_='items').find('p', class_='label', string='Private price guide **')
                    if private_price_guide_element:
                        private_price_guide = private_price_guide_element.find_next('p', class_='highlight-text').text.strip()

                    # Extract image URL
                    image_element = soup.find('img', class_='item-image')
                    if image_element:
                        image_url = image_element['src']

                    # Save the website content to output.html
                    with open('output.html', 'w', errors='ignore') as file:
                        # Include the extracted data in the output.html file
                        file.write(f"Price when new (EGC): {price_when_new}\n")
                        file.write(f"Private price guide: {private_price_guide}\n")
                        file.write(f"Image URL: {image_url}\n\n")
                        file.write(html_content)

                    # Break the loop since a matching body type is found
                    break
                else:
                    print(f"HTML file {optionstring} does not contain the bodytype: {bodytype}")
            else:
                print("No title found for", url)
    except Exception as ex:
        print(f"An error occurred for {url}: {ex}")

# Check if a matching body type was found
if not matching_body_type_found:
    print(f"No website with the bodytype '{bodytype}' was found.")

# Load the HTML content from output.html with the specified encoding
with open('output.html', 'r', encoding='utf-8-sig', errors='ignore') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Function to find elements case-insensitively
def find_element_case_insensitive(tag_name, text):
    elements = soup.find_all(lambda tag: tag.name.lower() == tag_name.lower() and text.lower() in tag.get_text().lower())
    return elements

# Extract the price when new (EGC)
price_when_new_elements = find_element_case_insensitive('p', 'Price when new (EGC) ^')
if price_when_new_elements:
    price_when_new = price_when_new_elements[0].find_next('p', class_='highlight-text')
    if price_when_new:
        price_when_new = price_when_new.text.strip()
    else:
        price_when_new = "N/A"
else:
    price_when_new = "N/A"

# Extract the private price guide
private_price_guide_elements = find_element_case_insensitive('p', 'Private price guide **')
if private_price_guide_elements:
    private_price_guide = private_price_guide_elements[0].find_next('p', class_='highlight-text')
    if private_price_guide:
        private_price_guide = private_price_guide.text.strip()
    else:
        private_price_guide = "N/A"
else:
    private_price_guide = "N/A"

# Extract the image URL
image_element = soup.find('img', class_='item-image')
if image_element:
    image_url = image_element['src']
else:
    image_url = ""

# Create an HTML template with extracted information and a modern style
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Car Information</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .container {{
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.2);
            padding: 20px;
            text-align: center;
        }}
        .highlight-text {{
            color: #007BFF;
        }}
        .car-image {{
            max-width: 100%;
            height: auto;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Car Information</h1>
        <p><strong>Price when new (EGC):</strong> <span class="highlight-text">{price_when_new}</span></p>
        <p><strong>Private price guide:</strong> <span class="highlight-text">{private_price_guide}</span></p>
        <img class="car-image" src="{image_url}" alt="Car Image">
    </div>
</body>
</html>
"""

# Save the HTML template to car_info.html
with open('car_info.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_template)

print("Car information has been saved to car_info.html.")