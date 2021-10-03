from datetime import date
from io import BytesIO
from zipfile import ZipFile
from requests.auth import HTTPBasicAuth
import urllib, base64
import requests
from shutil import copyfile
from os import listdir
from os.path import isfile, join
import subprocess
mail = "manwar.hamza@gmail.com"

def download_and_unzip(url, extract_to='.'):
    request = urllib.request.Request(url)
    p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, url, mail, mail)
    handler = urllib.request.HTTPBasicAuthHandler(p)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)
    http_response = urllib.request.urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)
    onlyfiles = [f for f in listdir(extract_to) if isfile(join(extract_to, f))]
    for i in onlyfiles:
        if "Percent.tif" in i:
            copyfile(i, "/home/manwar/GIS/IMERG.tif")
            subprocess.check_call("sudo apachectl restart".split())
    

today = date.today()
today = today.strftime("%Y/%m")
url = 'https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/' + str(today)
files = requests.get(url, auth=HTTPBasicAuth(mail, mail)).text

final_file = ""
for i in files.split(".zip\""):
    file = i.split("\"")[-1]
    if file[:2] == '3B':
        final_file = file + ".zip"

download_and_unzip(url + "/" + final_file)
