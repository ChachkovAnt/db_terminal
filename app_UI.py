from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QWidget, QPushButton, QDesktopWidget, QTreeWidget,
                             QGridLayout, QLabel, QHeaderView, QLineEdit)


class UI(QWidget):

    def __init__(self):
        super().__init__()

        self.remote_tree = None
        self.local_tree = None

        self.grid = None

        self.initUI()

    def initUI(self):

        self.resize(1000, 500)
        self.center()
        self.setWindowTitle('Database redactor')

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.init_buttons()
        self.init_tree_views()

        self.setLayout(self.grid)

        self.show()

    def init_buttons(self):
        # DOWNLOAD
        self.download_btn = QPushButton('<<<', self)
        self.grid.addWidget(self.download_btn, 1, 6)

        # PLUS
        self.plus_btn = QPushButton('+', self)
        self.grid.addWidget(self.plus_btn, 10, 1)

        # MINUS
        self.minus_btn = QPushButton('-', self)
        self.grid.addWidget(self.minus_btn, 10, 2)

        # RENAME(a)
        self.rename_btn = QPushButton('a', self)
        self.grid.addWidget(self.rename_btn, 10, 3)

        # APPLY
        self.apply_btn = QPushButton('Apply', self)
        self.grid.addWidget(self.apply_btn, 10, 4)

        # RESET
        self.reset_btn = QPushButton('Reset', self)
        self.grid.addWidget(self.reset_btn, 10, 5)

    def init_tree_views(self):

        self.remote_tree = QTreeWidget(self)
        self.remote_tree.clear()
        self.remote_tree.setHeaderLabels(['Remote database view', 'Id', 'Value'])
        self.remote_tree.setColumnCount(3)
        self.remote_tree.setColumnWidth(0, 180)
        self.remote_tree.setColumnWidth(1, QHeaderView.ResizeToContents)
        self.remote_tree.setColumnWidth(2, QHeaderView.ResizeToContents)
        self.grid.addWidget(self.remote_tree, 0, 7, 5, 5)

        self.local_tree = QTreeWidget(self)
        self.local_tree.clear()
        self.local_tree.setHeaderLabels(['Local cache view', 'Id', 'Value'])
        self.local_tree.setColumnCount(3)
        self.local_tree.setColumnWidth(0, 180)
        self.local_tree.setColumnWidth(1, QHeaderView.ResizeToContents)
        self.local_tree.setColumnWidth(2, QHeaderView.ResizeToContents)
        self.grid.addWidget(self.local_tree, 0, 1, 5, 5)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class NameValDialog(QWidget):

    resultOk = pyqtSignal(str, str)

    def __init__(self, default_name='', default_val=''):
        super().__init__()
        self.default_val = default_val
        self.default_name = default_name
        self.grid = None
        self.initUI()
        self.cancel_btn.clicked.connect(self.close)
        self.ok_btn.clicked.connect(self.return_msg)

    def initUI(self):
        self.resize(200, 100)
        self.center()
        self.setWindowTitle('Change name/value')

        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        self.init_buttons()
        self.init_line_edit()

        self.setLayout(self.grid)

        self.show()

    def init_buttons(self):
        self.ok_btn = QPushButton('OK', self)
        self.grid.addWidget(self.ok_btn, 4, 0)

        self.cancel_btn = QPushButton('Cancel', self)
        self.grid.addWidget(self.cancel_btn, 4, 1)

    def init_line_edit(self):
        self.qle1 = QLineEdit(self.default_name, self)
        self.grid.addWidget(self.qle1, 1, 0, 1, 2)
        self.grid.addWidget(QLabel('Enter name:'), 0, 0)

        self.qle2 = QLineEdit(self.default_val, self)
        self.grid.addWidget(self.qle2, 3, 0, 1, 2)
        self.grid.addWidget(QLabel('Enter value:'), 2, 0)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def return_msg(self):
        name = self.qle1.text()
        value = self.qle2.text()

        self.resultOk.emit(name, value)
        self.close()

