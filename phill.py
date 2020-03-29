import pywikibot as pwb
import wikitextparser as wtp
import requests
import urllib.request
from pathlib import Path
import simpleaudio as sa
from PhillApp import *

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout d'une prononciation phonétique (via PhiLL v{VERSION})"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Gathering data from the Wiktionary
site = pwb.Site()
category = pwb.Category(site, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")

tasks = []


def extract_templates(wikicode):
    # Travel all the sections to find the language section we want

    for lang_section in wikicode.sections:
        if lang_section.title.replace(" ", "").lower() == "{{langue|fr}}":
            return lang_section.templates

    # There is no section with that language (which is weird??)
    return None


def pick_new_tasks(max_tasks=1):
    tasks_count = 0
    for page in category.articles(startprefix='t'):
        if page.namespace() == 0:
            for template in extract_templates(wtp.parse(page.text)):
                # Get the "écouter" templates to gather the tasks
                if template.name.lower() == "écouter":
                    for arg in template.arguments:
                        if arg.name.lower() == "audio":
                            tasks.append((page.title(), arg.value))
                            tasks_count += 1
        if tasks_count >= max_tasks:
            break


def download_file():
    task = tasks[0]
    Path('cache/' + task[0]).mkdir(parents=True, exist_ok=True)
    r = requests.get(COMMONS_API, params={'action': 'query',
                                          'format': 'json',
                                          'prop': 'imageinfo',
                                          'iiprop': 'url',
                                          'titles': 'File:' + task[1]})
    for fileid in r.json()['query']['pages'].values():
        url = fileid['imageinfo'][0]['url']
        urllib.request.urlretrieve(url, filename="cache/" + task[0] + "/" + task[1])


def play_task_file():
    task = tasks[0]
    wave_obj = sa.WaveObject.from_wave_file("cache/" + task[0] + "/" + task[1])
    wave_obj.play()


def confirm_ipa():
    r = requests.get("http://darmo-creations.herokuapp.com/ipa-generator/to-ipa/",
                     params={'input': text_zone.text()})
    ipa = r.json()['ipa_code']

    answer = QMessageBox.question(
        window, None,
        f"L'API récupérée est {ipa}. Est-ce correct?",
        QMessageBox.Ok | QMessageBox.Cancel
    )
    if answer & QMessageBox.Ok:
        complete_task(ipa)
    elif answer & QMessageBox.Cancel:
        return


def complete_task(ipa):
    task = tasks[0]
    page = pwb.Page(site, task[0])

    wikicode = wtp.parse(page.text)
    for section in wikicode.sections:
        if section.title.replace(" ", "").lower() == "{{langue|fr}}":
            for template in section.templates:
                for arg in template.arguments:
                    if arg.name.lower() == "audio" and arg.value == task[1]:
                        template.set_arg("pron", ipa)
                        break

    page.text = str(wikicode)

    page.save(SUMMARY, minor=False)

    tasks.remove(task)

def start_tasks():
    pick_new_tasks()


# GUI:
app = QApplication([])
app.setApplicationName("Phonetica in Lingua Libre (PhiLL) v" + VERSION)
app.setApplicationVersion(VERSION)
window = PhillApp()
app.exec_()

# IPA entry text zone
text_zone = QLineEdit()
