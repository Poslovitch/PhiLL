from PyQt5.QtWidgets import *


class PhillApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tasks = []

        self.setCentralWidget(WelcomeScreen(self))
        self.show()



class WelcomeScreen(QWidget):

    def __init__(self, phill):
        super().__init__(parent=phill)
        label = QLabel("Bonjour ! Bienvenue sur PhiLL.\n"
                       f"Il y a %pages% prononciations phonologiques manquantes en français.\n"
                       "Êtes-vous prêt au départ pour votre aventure phonologique ?")

        # category.categoryinfo['pages']

        start_button = QPushButton("C'est parti !")
        # start_button.clicked.connect(start_tasks)

        layout = QVBoxLayout()

        layout.addWidget(label)
        layout.addWidget(start_button)

        self.setLayout(layout)