import sys
from PyQt5.QtWidgets import QApplication
from app_control import MyApp
from app_model import DBManager

def main():
    app = QApplication(sys.argv)
    ex = MyApp(DBManager())
    app.exec_()



if __name__ == '__main__':
    sys.exit(main())
