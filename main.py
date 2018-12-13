import sys
from PyQt5.QtWidgets import QApplication
from app_control import MyApp
from app_model import DBManager


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    ex = MyApp(DBManager())
    app.exec_()


if __name__ == '__main__':
    sys.excepthook = except_hook
    sys.exit(main())
