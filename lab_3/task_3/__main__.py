import sys

from PyQt5 import QtWidgets

from .app import Window

app = QtWidgets.QApplication(sys.argv)
w = Window()
w.resize(650, 400)
w.show()
app.exec_()
