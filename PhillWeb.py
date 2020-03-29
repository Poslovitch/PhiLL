import requests
import urllib.request
from pathlib import Path

COMMONS_API = "https://commons.wikimedia.org/w/api.php"


def translate_code_to_ipa(code: str) -> str:
    r = requests.get("http://darmo-creations.herokuapp.com/ipa-generator/to-ipa/",
                     params={'input': code})
    return r.json()['ipa_code']


def translate_ipa_to_code(ipa: str) -> str:
    r = requests.get("http://darmo-creations.herokuapp.com/ipa-generator/from-ipa/",
                     params={'input': ipa})
    return r.json()['ipa_code']


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
