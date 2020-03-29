from PyQt5.QtWidgets import *


class PhillApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tasks = [("table de vérité", "LL-Q150 (fra)-WikiLucas00-table de vérité.wav")]

        self.setCentralWidget(WelcomeScreen(self))
        self.show()

    def show_tasks_list(self):
        self.setCentralWidget(TasksListScreen(self))

    def show_task(self):
        self.setCentralWidget(TaskScreen(self, self.tasks[0]))


class WelcomeScreen(QWidget):

    def __init__(self, phill_app):
        super().__init__()
        label = QLabel("Bonjour ! Bienvenue sur PhiLL.\n"
                       f"Il y a %pages% prononciations phonologiques manquantes en français.\n"
                       "Êtes-vous prêt au départ pour votre aventure phonologique ?")

        # category.categoryinfo['pages']

        start_button = QPushButton("C'est parti !")
        start_button.clicked.connect(phill_app.show_tasks_list)

        layout = QVBoxLayout()

        layout.addWidget(label)
        layout.addWidget(start_button)

        self.setLayout(layout)


class TasksListScreen(QWidget):

    def __init__(self, phill_app):
        super().__init__()

        layout = QVBoxLayout()

        label_intro = QLabel(f"Il y a {len(phill_app.tasks)} tâches à compléter.")

        label_tasks = QLabel()

        _tasks = ""
        for task in phill_app.tasks:
            _tasks += f"- {task[0]} : {task[1]}\n"

        label_tasks.setText(_tasks)

        button_start = QPushButton("Lancer la première tâche")
        button_start.clicked.connect(phill_app.show_task)

        layout.addWidget(label_intro)
        layout.addWidget(label_tasks)
        layout.addWidget(button_start)

        self.setLayout(layout)


class TaskScreen(QWidget):

    def __init__(self, phill_app, task):
        super().__init__()
        layout = QVBoxLayout()

        label_name = QLabel(task[0] + " (" + task[1] + ")")

        button_play = QPushButton("Lire l'audio")
        # button_play.clicked.connect(play_task_file)

        label_explain = QLabel("Entrez la prononciation en API (utilisez la syntaxe de Darmo) :")

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(task[0])

        button_fetch_ipa = QPushButton("Transcrire en API")
        # button_fetch_ipa.clicked.connect(confirm_ipa)

        layout.addWidget(label_name)
        layout.addWidget(button_play)
        layout.addWidget(label_explain)
        layout.addWidget(self.line_edit)
        layout.addWidget(button_fetch_ipa)

        self.setLayout(layout)
