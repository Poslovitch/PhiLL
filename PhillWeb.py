import requests
import urllib.request
from pathlib import Path

COMMONS_API = "https://commons.wikimedia.org/w/api.php"


def download_commons_file(sub_folder: str, file_name: str):
    Path('cache/' + sub_folder).mkdir(parents=True, exist_ok=True)
    r = requests.get(COMMONS_API, params={'action': 'query',
                                          'format': 'json',
                                          'prop': 'imageinfo',
                                          'iiprop': 'url',
                                          'titles': 'File:' + file_name})
    for fileid in r.json()['query']['pages'].values():
        url = fileid['imageinfo'][0]['url']
        urllib.request.urlretrieve(url, filename="cache/" + sub_folder + "/" + file_name)
