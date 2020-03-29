import pywikibot as pwb
import wikitextparser as wtp
from PhillApp import *

VERSION = "0.0.1"
SUMMARY = f"/* Prononciation */ Ajout d'une prononciation phonétique (via PhiLL v{VERSION})"

# Gathering data from the Wiktionary
site = pwb.Site()
category = pwb.Category(site, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")

tasks = []


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


# GUI:
app = QApplication([])
app.setApplicationName("Phonetica in Lingua Libre (PhiLL) v" + VERSION)
app.setApplicationVersion(VERSION)
window = PhillApp(VERSION)
app.exec_()