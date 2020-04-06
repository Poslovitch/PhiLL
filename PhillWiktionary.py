import pywikibot as pwb
import wikitextparser as wtp


class PhillWiktionary:

    def __init__(self, phill_ver: str, category_name: str):
        self.SUMMARY = f"/* Prononciation */ Prononciation phonétique (via PhiLL v{phill_ver})"

        self.site = pwb.Site()
        self.category = pwb.Category(self.site, category_name)

        self.start_prefix = ''

    def get_remaining_pages(self) -> int:
        return self.category.categoryinfo['pages']

    def pick_new_tasks(self, start_from: str = '', max_pages: int = 5):
        new_tasks = []
        pages_count = 0

        if start_from:
            self.start_prefix = start_from

        for page in self.category.articles(startprefix=self.start_prefix):
            if page.namespace() == 0:
                page_tasks = self.extract_tasks(page)
                if len(page_tasks) > 0:
                    pages_count += 1
                    new_tasks.extend(page_tasks)

                if pages_count >= max_pages:
                    self.start_prefix = page.title()
                    break

        return new_tasks

    def is_template_valid(self, template) -> bool:
        # Check the arg "2" and "pron": if they exist and are not empty -> invalid
        if template.has_arg("2"):
            if len(template.get_arg("2").value.replace(" ", "")) > 0:
                return False
        if template.has_arg("pron"):
            if len(template.get_arg("pron").value.replace(" ", "")) > 0:
                return False

        # If there is no audio, invalid as well
        if (not template.has_arg("audio")) or (len(template.get_arg("audio").value.replace(" ", "")) == 0):
            return False

        return True

    @staticmethod
    def extract_prototypical_pronunciation(page: pwb.Page) -> str:
        wikicode = wtp.parse(page.text)

        for section in wikicode.sections:
            if section.title.replace(" ", "").lower() == "{{langue|fr}}":
                for template in section.templates:
                    if template.name.lower() == "pron":
                        return template.get_arg("1").value

    def extract_tasks(self, page: pwb.Page) -> list:
        templates = []
        page_tasks = []
        prototypical_pronunciation = self.extract_prototypical_pronunciation(page)

        wikicode = wtp.parse(page.text)
        # Gather all the {{écouter}}
        for section in wikicode.sections:
            if section.title.replace(" ", "").lower() == "{{langue|fr}}":
                for template in section.templates:
                    if template.name.lower() == "écouter":
                        templates.append(template)

        for template in templates:
            if self.is_template_valid(template):
                task = (page.title(), template.get_arg("audio").value)
                if prototypical_pronunciation:
                    task = (page.title(), template.get_arg("audio").value, prototypical_pronunciation)
                page_tasks.append(task)

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
                                page.text = str(wikicode).replace(str(template), str(self.update_template(template, task[2])))
                                break

            page.save(self.SUMMARY, minor=False)

        completed_tasks.clear()

    def update_template(self, template: wtp.Template, ipa: str):
        # add pron and remove 2
        template.set_arg("pron", ipa)
        template.del_arg("2")

        # sort all the arguments
        sorted_args = sorted(template.arguments, key=self.sort_template_arguments)

        new_template = "{{écouter"
        for arg in sorted_args:
            new_template += str(arg)
        new_template += "}}"

        return new_template

    @staticmethod
    def sort_template_arguments(arg: wtp.Argument):
        priority = ["1", "pron", "3", "lang", "audio", "titre"]
        return priority.index(arg.name)
