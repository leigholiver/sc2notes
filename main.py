import sys, qdarkstyle
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mw = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()