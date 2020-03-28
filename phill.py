import pywikibot as pwb
import wikitextparser as wtp
import requests
import urllib.request
from pathlib import Path
import simpleaudio as sa
from PyQt5.QtWidgets import *

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout d'une prononciation phonétique (via PhiLL v{VERSION})."
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
    open_tasks_list()


def do_task():
    task = tasks[0]
    download_file()
    play_task_file()

    lay = QVBoxLayout()

    label_name = QLabel(task[0] + " (" + task[1] + ")")

    button_play = QPushButton("Lire l'audio")
    button_play.clicked.connect(play_task_file)

    label_explain = QLabel("Entrez la prononciation en API (utilisez la syntaxe de Darmo) :")

    text_zone.setPlaceholderText(task[0])

    button_fetch_ipa = QPushButton("Transcrire en API")
    button_fetch_ipa.clicked.connect(confirm_ipa)

    lay.addWidget(label_name)
    lay.addWidget(button_play)
    lay.addWidget(label_explain)
    lay.addWidget(text_zone)
    lay.addWidget(button_fetch_ipa)

    widget2 = QWidget()
    widget2.setLayout(lay)
    window.setCentralWidget(widget2)


def start_tasks():
    pick_new_tasks()
    open_tasks_list()


def open_tasks_list():
    lay = QVBoxLayout()

    label_intro = QLabel(f"Il y a {len(tasks)} tâches à compléter.")

    label_tasks = QLabel()

    _tasks = ""
    for task in tasks:
        _tasks += f"- {task[0]} : {task[1]}\n"

    label_tasks.setText(_tasks)

    button_start = QPushButton("Lancer la première tâche")
    button_start.clicked.connect(do_task)

    lay.addWidget(label_intro)
    lay.addWidget(label_tasks)
    lay.addWidget(button_start)

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

# IPA entry text zone
text_zone = QLineEdit()

app.exec_()