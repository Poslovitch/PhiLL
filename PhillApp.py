from PyQt5.QtWidgets import *
import PhillAudio
import PhillWeb
import PhillWiktionary as PhWikt


class PhillApp(QMainWindow):

    def __init__(self, version):
        super().__init__()

        self.wiktionary = PhWikt.PhillWiktionary(version, "Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français")
        self.pending_tasks = self.wiktionary.pick_new_tasks()
        self.completed_tasks = []

        self.setCentralWidget(WelcomeScreen(self))
        self.show()

    def show_tasks_list(self):
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

        start_button = QPushButton("C'est parti !")
        start_button.clicked.connect(phill_app.show_tasks_list)

        layout = QVBoxLayout()

        layout.addWidget(label)
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

        label_explain = QLabel("Entrez la prononciation en API (utilisez la syntaxe de Darmo) :")

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(task[0])

        button_fetch_ipa = QPushButton("Transcrire en API")
        button_fetch_ipa.clicked.connect(self.confirm_ipa)

        layout.addWidget(label_name)
        layout.addWidget(button_play)
        layout.addWidget(label_explain)
        if len(task) == 3:
            # task has a prototypical pronunciation
            prototypical_pronunciation = task[2].replace('t', 't̪').replace('d', 'd̪').replace('l', 'l̪').replace('n', 'n̪')
            self.prototypical_pronunciation_code = PhillWeb.translate_ipa_to_code(prototypical_pronunciation)

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

    def import_prototypical_pronunciation(self):
        self.line_edit.setText(self.prototypical_pronunciation_code)

    def play_file(self):
        PhillAudio.play_wav_file(self.task[0], self.task[1])

    def confirm_ipa(self):
        ipa = PhillWeb.translate_code_to_ipa(self.line_edit.text())
        answer = QMessageBox.question(
            self, None,
            f"La prononciation entrée est {ipa}. Est-ce correct?",
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
