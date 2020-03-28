import pywikibot as pwb
import wikitextparser as wtp
import requests
import urllib.request
from pathlib import Path
import simpleaudio as sa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout de la prononciation phonétique pour $1 enregistrement(s) (via PhiLL v{VERSION})."
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Gathering data from the Wiktionary
site = pwb.Site()
category = pwb.Category(site, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")

tasks = []


def extract_templates(wikicode):
    # Travel all the sections to find the language section we want

    for lang_section in wikicode.sections:
        if lang_section.title.replace(" ", "").lower() == "{{langue|fr}}":
            return wtp.parse(lang_section.contents).templates

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


def do_task(task):
    return


def start_tasks():
    pick_new_tasks()
    lay = QVBoxLayout()

    label_intro = QLabel(f"Il y a {len(tasks)} tâches à compléter.")

    label_tasks = QLabel()

    _tasks = ""
    for task in tasks:
        _tasks += f"- {task[0]} : {task[1]}\n"

    label_tasks.setText(_tasks)

    lay.addWidget(label_intro)
    lay.addWidget(label_tasks)

    widget2 = QWidget()
    widget2.setLayout(lay)
    window.setCentralWidget(widget2)


# GUI:
app = QApplication([])
app.setApplicationName("Phonetica in Lingua Libre (PhiLL)")
app.setApplicationVersion(VERSION)

label = QLabel("Bonjour ! Bienvenue sur PhiLL.\n"
               f"Il y a {category.categoryinfo['pages']} prononciations phonologiques manquantes en français.\n"
               "Êtes-vous prêt au départ pour votre aventure phonologique ?")

start_button = QPushButton("C'est parti !")
start_button.clicked.connect(start_tasks)

layout = QVBoxLayout()

layout.addWidget(label)
layout.addWidget(start_button)

widget = QWidget()
widget.setLayout(layout)

window = QMainWindow()
window.setCentralWidget(widget)
window.show()

count = 0
LIMIT = -1


app.exec_()

# for page in category.articles(startprefix='t'):
#     if count > LIMIT:
#         break
#
#     if page.namespace() == 0:
#         page_title = page.title().replace(' ', '_')
#         print(page_title)
#         Path('cache/' + page_title).mkdir(parents=True, exist_ok=True)
#
#         wikicode = wtp.parse(page.text)
#         section = get_pronunciation_section(wikicode, 'fr')
#
#         section_code = wtp.parse(section.contents)
#         for template in section_code.templates:
#             if template.name.lower() == "écouter":
#                 for arg in template.arguments:
#                     if arg.name.lower() == "audio":
#                         print(arg.value)
#                         r = requests.get(COMMONS_API, params={'action': 'query',
#                                                               'format': 'json',
#                                                               'prop': 'imageinfo',
#                                                               'iiprop': 'url',
#                                                               'titles': 'File:' + arg.value})
#                         for fileid in r.json()['query']['pages'].values():
#                             url = fileid['imageinfo'][0]['url']
#                             urllib.request.urlretrieve(url, filename="cache/" + page_title + "/" + arg.value)
#
#                             wave_obj = sa.WaveObject.from_wave_file("cache/" + page_title + "/" + arg.value)
#                             play_obj = wave_obj.play()
#                             play_obj.wait_done()
#
#                             api = input("Tapez en API: ")
#                             r2 = requests.get("http://darmo-creations.herokuapp.com/ipa-generator/to-ipa/",
#                                               params={'input': api})
#                             print(r2.json()['ipa_code'])
#         count += 1
