from PyQt5.QtWidgets import *
import webbrowser
import PhillAudio
import PhillWeb
import PhillWiktionary as PhWikt
import PhillIPA


class PhillApp(QMainWindow):

    def __init__(self, version):
        super().__init__()

        self.wiktionary = PhWikt.PhillWiktionary(version, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")
        self.pending_tasks = []
        self.completed_tasks = []
        self.first_time = True

        self.welcome_screen = WelcomeScreen(self)

        self.setCentralWidget(self.welcome_screen)
        self.show()

    def show_tasks_list(self):
        if self.first_time:
            self.pending_tasks = self.wiktionary.pick_new_tasks(self.welcome_screen.start_from.text(), 4)
            self.first_time = False
        elif len(self.pending_tasks) <= 3:
            print('there is less than 3 tasks')
            # self.pending_tasks.append(self.wiktionary.pick_new_tasks(max_pages=1))
        self.setCentralWidget(TasksListScreen(self))

    def show_task(self):
        self.setCentralWidget(TaskScreen(self, self.pending_tasks[0]))


class WelcomeScreen(QWidget):

    def __init__(self, phill_app: PhillApp):
        super().__init__()
        label = QLabel("Bonjour ! Bienvenue sur PhiLL.\n"
                       f"Il y a {phill_app.wiktionary.get_remaining_pages()} pages sur lesquelles des prononciations"
                       " phonétiques ne sont pas renseignées.\n"
                       "Êtes-vous prêt au départ pour votre aventure phonologique ?")

        self.start_from = QLineEdit()
        # self.start_from.setText("a")

        start_button = QPushButton("C'est parti !")
        start_button.clicked.connect(phill_app.show_tasks_list)

        layout = QVBoxLayout()

        layout.addWidget(label)
        layout.addWidget(self.start_from)
        layout.addWidget(start_button)

        self.setLayout(layout)


class TasksListScreen(QWidget):

    def __init__(self, phill_app: PhillApp):
        super().__init__()

        layout = QVBoxLayout()

        label_intro = QLabel(f"Il y a {len(phill_app.pending_tasks)} tâches à compléter.")

        label_tasks = QLabel()

        _tasks = ""
        for task in phill_app.pending_tasks:
            _tasks += f"- {task[0]} : {task[1]}\n"

        label_tasks.setText(_tasks)

        button_start = QPushButton("Lancer la première tâche")
        button_start.clicked.connect(phill_app.show_task)

        layout.addWidget(label_intro)
        layout.addWidget(label_tasks)
        layout.addWidget(button_start)

        self.setLayout(layout)


class TaskScreen(QWidget):

    def __init__(self, phill_app: PhillApp, task):
        super().__init__()
        self.task = task
        self.phill_app = phill_app
        self.prototypical_pronunciation_code = ""
        self.download_file()
        layout = QVBoxLayout()

        label_name = QLabel(task[0] + " (" + task[1] + ")")

        button_play = QPushButton("Lire l'audio")
        button_play.clicked.connect(self.play_file)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(task[0])

        button_fetch_ipa = QPushButton("Transcrire en API")
        button_fetch_ipa.clicked.connect(self.confirm_ipa)

        layout.addWidget(label_name)
        layout.addWidget(button_play)

        layout_darmo = QHBoxLayout()

        label_explain = QLabel("Entrez la prononciation en API dans le champ texte\n"
                               "ci-dessous (utilisez la syntaxe de Darmo) :")
        layout_darmo.addWidget(label_explain)

        button_darmo_syntax = QPushButton("Documentation sur la syntaxe de Darmo")
        button_darmo_syntax.clicked.connect(self.open_darmo_website)
        layout_darmo.addWidget(button_darmo_syntax)

        layout.addLayout(layout_darmo)
        if len(task) == 3:
            # task has a prototypical pronunciation
            prototypical_pronunciation = task[2].replace('t', 't̪').replace('d', 'd̪').replace('l', 'l̪').replace('n', 'n̪')
            self.prototypical_pronunciation_code = PhillIPA.ipa_to_code(prototypical_pronunciation)

            sub_layout = QHBoxLayout()

            label_use_ipp = QLabel("Importez la prononciation prototypique adaptée à la phonologie française [" +
                                   prototypical_pronunciation + "] avec le bouton IPP.")
            layout.addWidget(label_use_ipp)

            button_use_existing_ipa = QPushButton("IPP")
            button_use_existing_ipa.clicked.connect(self.import_prototypical_pronunciation)

            sub_layout.addWidget(self.line_edit)
            sub_layout.addWidget(button_use_existing_ipa)

            layout.addLayout(sub_layout)
        else:
            layout.addWidget(self.line_edit)

        layout.addWidget(button_fetch_ipa)

        self.setLayout(layout)
        self.play_file()

    @staticmethod
    def open_darmo_website():
        webbrowser.open("https://darmo-creations.herokuapp.com/ipa-generator/")

    def import_prototypical_pronunciation(self):
        self.line_edit.setText(self.prototypical_pronunciation_code)

    def play_file(self):
        PhillAudio.play_wav_file(self.task[0], self.task[1])

    def confirm_ipa(self):
        ipa = PhillIPA.code_to_ipa(self.line_edit.text())
        answer = QMessageBox.question(
            self, None,
            f"La prononciation entrée est [{ipa}]. Est-ce correct?",
            QMessageBox.Yes | QMessageBox.No
        )
        if answer & QMessageBox.Yes:
            self.complete_task(ipa)
        elif answer & QMessageBox.No:
            return

    def download_file(self):
        PhillWeb.download_commons_file(self.task[0], self.task[1])

    def complete_task(self, ipa: str):
        self.phill_app.completed_tasks.append((self.task[0], self.task[1], ipa))
        self.phill_app.pending_tasks.remove(self.task)
        self.phill_app.wiktionary.apply_completed_tasks(self.phill_app.completed_tasks)
        self.phill_app.show_tasks_list()
