import pywikibot as pwb
import wikitextparser as wtp
from PhillApp import *

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout d'une prononciation phonétique (via PhiLL v{VERSION})"

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