import sys
import os
import traceback
from PyQt5 import QtGui, QtWidgets
from views.ui import Ui_MainWindow
import resources  # noqa

if sys.platform == 'win32':
    path = r"C:\Program Files\Graphviz\bin"
    if os.path.isdir(path) and path not in os.environ['PATH']:
        os.environ['PATH'] += f";{path}"

    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.jdeweeselab.pcviewer")
    except ImportError:
        pass


# Catches exceptions to print in the output window instead of crashing the app
def excepthook(ty, val, tb):
    tb = "".join(traceback.format_exception(ty, val, tb))
    print(f"PSICalc Viewer error:\n {tb}")


sys.excepthook = excepthook
app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon(":icons/icon.ico"))
window = Ui_MainWindow()
window.show()
app.exec()
