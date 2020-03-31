from PhillApp import *

VERSION = "0.0.1"

# GUI:
app = QApplication([])
app.setApplicationName("Phonetica in Lingua Libre (PhiLL) v" + VERSION)
app.setApplicationVersion(VERSION)
window = PhillApp(VERSION)
app.exec_()
