from app_UI import UI, NameValDialog
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt


class MyApp(UI):
    """
    Class MyApp binds UI and the model.
    """
    def __init__(self, db_manager):
        """
        Add into MyApp db_manager model and create an empty storage for
        QTreeWidgetItem
        :return: None
        """
        super().__init__()

        self.db_control = db_manager
        self.tree_storage = dict()
        self.download_base()

    def init_buttons(self):
        """
        It complements parent method the connection of UI signals and controllers slots
        :return: None
        """
        super().init_buttons()
        self.download_btn.clicked.connect(self.on_download_clicked)
        self.plus_btn.clicked.connect(self.on_plus_btn_clicked)
        self.minus_btn.clicked.connect(self.on_minus_btn_clicked)
        self.rename_btn.clicked.connect(self.on_rename_btn_clicked)
        self.apply_btn.clicked.connect(self.on_apply_btn_clicked)
        self.reset_btn.clicked.connect(self.on_reset_btn_clicked)

    def download_base(self):
        """
        Performs downloading standart base from json.
        :return: None
        """
        self.renew_tree('remote', self.db_control.get_remote_storage())

    def renew_tree(self, tree, data=None):
        """
        Renew data in QTreeWidget. If tree is not local or remote, data will be reset.
        :param tree: 'local'/'remote'/'any'
        :param data: dict
        :return: None
        """
        if tree == 'local':
            treeview = self.local_tree
        elif tree == 'remote':
            treeview = self.remote_tree
        else:
            self.local_tree.clear()
            self.remote_tree.clear()
            return

        self.tree_storage = dict()
        treeview.clear()
        self.make_items(treeview, data)

    def make_items(self, tree, data):
        """
        Makes items one by one.
        :param tree: local or remote QTreeWidget object
        :param data: data from base in dictionary format
        :return: None
        """
        for item_id, item_raw in data.items():
            self.make_qitem(item_raw, tree, data)

    def make_qitem(self, item_raw, tree, data):
        """
        Makes QTreeWidgetItem and adds it to treeView storage.
        :param item_raw: item, packed in dictionary
        :param tree: local or remote QTreeWidget object
        :param data: data from base in dictionary format
        :return: None
        """
        store = self.tree_storage
        parent_id = item_raw['parent']
        item_id = item_raw['id']
        deleted = item_raw['deleted']

        if item_id not in store:
            if parent_id in data and parent_id in store:
                store[item_id] = QTreeWidgetItem(store[parent_id])
            elif parent_id in data and parent_id not in store:
                self.make_qitem(data[parent_id], tree, data)
                store[item_id] = QTreeWidgetItem(store[parent_id])
            else:
                store[item_id] = QTreeWidgetItem(tree)

        store[item_id].setData(0, 0, item_raw['name'])
        store[item_id].setData(1, 0, item_id)
        store[item_id].setData(2, 0, item_raw['value'])
        store[item_id].setExpanded(True)
        if deleted:
            store[item_id].setBackground(0, Qt.red)
            store[item_id].setBackground(1, Qt.red)
            store[item_id].setBackground(2, Qt.red)

    def get_current_id(self, tree='remote'):
        """
        Allows to get selected item's id.
        :param tree: 'local'/'remote'
        :return: None
        """
        if tree == 'remote':
            item = self.remote_tree.currentItem()
        else:
            item = self.local_tree.currentItem()
        if item:
            return item.text(1)
        else:
            return None

    def get_current_name(self):
        """
        Allows to get selected item's name in the local treeView.
        :return: None
        """
        item = self.local_tree.currentItem()
        if item:
            return item.text(0)
        else:
            return None

    def get_current_value(self):
        """
        Allows to get selected item's name in the local treeView
        :return: None
        """
        item = self.local_tree.currentItem()
        if item:
            return item.text(2)
        else:
            return None

    def on_download_clicked(self):
        """
        Download button handler. It sends to db_control pull command and then renews the treeView.
        :return: None
        """
        if self.get_current_id(tree='remote'):
            tree, data = self.db_control.pull(self.get_current_id(tree='remote'))
            self.renew_tree(tree, data)

    def on_plus_btn_clicked(self):
        """
        Plus button handler. It sends to db_control add_item command and then renews the treeView
        :return: None
        """
        tree, data = self.db_control.add_item({'parent': self.get_current_id(tree='local')})
        self.renew_tree(tree, data)

    def on_minus_btn_clicked(self):
        """
        Minus button handler. It sends to db_control del_item command with
        current_id argument and then renews the treeView
        :return: None
        """
        tree, data = self.db_control.del_item(self.get_current_id(tree='local'))
        self.renew_tree(tree, data)

    def on_rename_btn_clicked(self):
        """
        Rename button handler. It calls dialog window, If something selected in local treeview,
        and then connects OK_button signal with slot send_changes.
        :return: None
        """
        if self.get_current_id(tree='local'):
            self.dlg = self.show_dialog()
            if self.dlg:
                self.dlg.resultOk.connect(self.send_changes)
                self.download_btn.setEnabled(False)

    def on_apply_btn_clicked(self):
        """
        Apply button handler. It sends commit command on db_control, then unlocks download button.
        :return: None
        """
        tree, data = self.db_control.commit()
        self.renew_tree(tree, data)
        tree, data = 'local', self.db_control.get_local_storage()
        self.renew_tree(tree, data)
        self.download_btn.setEnabled(True)

    def on_reset_btn_clicked(self):
        """
        Reset button handler. Sends reset command to model and renews trees.
        Then downloads standart database.
        :return: None
        """
        self.renew_tree(self.db_control.reset())
        self.download_base()

    def show_dialog(self):
        """
        Shows dialog for input name/value.
        :return: dia - dialog object(QWidget)
        """
        item_id = self.get_current_id(tree='local')
        default_name = self.get_current_name()
        default_val = self.get_current_value()

        deleted = self.db_control.is_deleted(item_id, store='local')

        if deleted:
            warn_text = 'Id{} was deleted. You can not change name or value.'.format(item_id)
            QMessageBox.critical(self, 'Message', warn_text)
            dia = None
        else:
            dia = NameValDialog(default_name, default_val)

        return dia

    def send_changes(self, name, value):
        """
        Sends name and value, which were changed in dialog window and renews treeView.
        :param name: 'any_name'
        :param value: 'any_value'
        :return: None
        """
        item_id = self.get_current_id(tree='local')
        tree, data = self.db_control.change_item(item_id, name=name, value=value)
        self.renew_tree(tree, data)
