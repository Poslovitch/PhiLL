import pywikibot as pwb
import wikitextparser as wtp
import requests
import urllib.request
from pathlib import Path
import simpleaudio as sa

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout de la prononciation phonétique pour $1 enregistrement(s) (via PhiLL v{VERSION})."
COMMONS_API = "https://commons.wikimedia.org/w/api.php"


def get_pronunciation_section(wikicode, lang):
    # Travel all the sections to find the language section we want

    for lang_section in wikicode.sections:
        if lang_section.title.replace(" ", "").lower() == "{{langue|" + lang + "}}":
            lang_section_content = wtp.parse(lang_section.contents)
            for pron_section in lang_section_content.sections:
                if pron_section.title.replace(" ", "").lower() == "{{s|prononciation}}":
                    return pron_section

    # There is no section with that language (which is weird??)
    return None


site = pwb.Site()
category = pwb.Category(site, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")

count = 0
LIMIT = 10

for page in category.articles(startprefix='t'):
    if page.namespace() == 0:
        page_title = page.title().replace(' ', '_')
        print(page_title)
        Path('cache/' + page_title).mkdir(parents=True, exist_ok=True)

        wikicode = wtp.parse(page.text)
        section = get_pronunciation_section(wikicode, 'fr')

        section_code = wtp.parse(section.contents)
        for template in section_code.templates:
            if template.name.lower() == "écouter":
                for arg in template.arguments:
                    if arg.name.lower() == "audio":
                        print(arg.value)
                        r = requests.get(COMMONS_API, params={'action': 'query',
                                                              'format': 'json',
                                                              'prop': 'imageinfo',
                                                              'iiprop': 'url',
                                                              'titles': 'File:' + arg.value})
                        for fileid in r.json()['query']['pages'].values():
                            url = fileid['imageinfo'][0]['url']
                            urllib.request.urlretrieve(url, filename="cache/" + page_title + "/" + arg.value)

                            wave_obj = sa.WaveObject.from_wave_file("cache/" + page_title + "/" + arg.value)
                            play_obj = wave_obj.play()
                            play_obj.wait_done()
        count += 1

    if count > LIMIT:
        break
