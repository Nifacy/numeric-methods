from PyQt5 import QtWidgets
from .app import Window
import sys


app = QtWidgets.QApplication(sys.argv)
w = Window()
w.resize(800, 500)
w.show()
app.exec_()
