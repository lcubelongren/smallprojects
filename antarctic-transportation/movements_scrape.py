
"""FLIGHTS"""
import numpy as np
import requests
from bs4 import BeautifulSoup
import numbers

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Load aircraft movements from local intranet
# Source: Naval Information Warfare Center (NIWC) 
# ------: POLAR PROGRAMS (NPP) CHARLESTON, SC

url_root = 'https://chm-mets-01-p.usap.gov'

# Return text urls

r = requests.get(url_root + '/mvmt/dailies', verify=False)
soup = BeautifulSoup(r.content, features='lxml')

hrefs_all = [soup.find_all('a')[i].get('href') 
             for i in range(len(soup.find_all('a')))]
hrefs_rel = [ha for ha in hrefs_all if ha[-5:] == 'daily']

for href in hrefs_rel:
	print(href.split('/')[2])
	r = requests.get(url_root + href, verify=False)
	soup = BeautifulSoup(r.content, features='lxml')
	output_fname = 'data/flights/{}.html'.format(href.split('/')[2])
	with open(output_fname, 'w', encoding='utf-8') as file:
    		file.write(str(soup))
