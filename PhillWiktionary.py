import pywikibot as pwb
import wikitextparser as wtp


class PhillWiktionary:

    def __init__(self, phill_ver: str, category_name: str):
        self.SUMMARY = f"/* Prononciation */ Prononciation phonétique (via PhiLL v{phill_ver})"

        self.site = pwb.Site()
        self.category = pwb.Category(self.site, category_name)

    def get_remaining_pages(self) -> int:
        return self.category.categoryinfo['pages']

    def pick_new_tasks(self, max_pages=5):
        new_tasks = []
        pages_count = 0

        for page in self.category.articles(startprefix='t'):
            if page.namespace() == 0:
                page_tasks = self.extract_tasks(page)
                if len(page_tasks) > 0:
                    pages_count += 1
                    new_tasks.extend(page_tasks)

            if pages_count >= max_pages:
                break

        return new_tasks

    def is_template_valid(self, template) -> bool:
        # Check the arg "2" and "pron": if they exist and are not empty -> invalid
        if template.get_arg("2") is not None:
            if len(template.get_arg("2").value.replace(" ", "")) > 0:
                return False
        if template.get_arg("pron") is not None:
            if len(template.get_arg("pron").value.replace(" ", "")) > 0:
                return False

        # If there is no audio, invalid as well
        if (template.get_arg("audio") is None) or (len(template.get_arg("audio").value.replace(" ", "")) == 0):
            return False

        return True

    def extract_tasks(self, page: pwb.Page) -> list:
        templates = []
        page_tasks = []

        wikicode = wtp.parse(page.text)
        # Gather all the {{écouter}}
        for section in wikicode.sections:
            if section.title.replace(" ", "").lower() == "{{langue|fr}}":
                for template in section.templates:
                    if template.name.lower() == "écouter":
                        templates.append(template)

        for template in templates:
            if self.is_template_valid(template):
                page_tasks.append((page.title(), template.get_arg("audio").value))

        return page_tasks

    def apply_completed_tasks(self, completed_tasks: list):
        for task in completed_tasks:
            page = pwb.Page(self.site, task[0])
            wikicode = wtp.parse(page.text)
            for section in wikicode.sections:
                if section.title.replace(" ", "").lower() == "{{langue|fr}}":
                    for template in section.templates:
                        for arg in template.arguments:
                            if arg.name.lower() == "audio" and arg.value == task[1]:
                                template.set_arg("pron", task[2])
                                break

            page.text = str(wikicode)

            page.save(self.SUMMARY, minor=False)

        completed_tasks.clear()
