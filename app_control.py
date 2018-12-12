from app_UI import UI, NameValDialog
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt


class MyApp(UI):
    def __init__(self, db_manager):
        super().__init__()

        self.db_control = db_manager
        self.tree_storage = dict()
        self.download_base()

    def init_buttons(self):
        super().init_buttons()
        self.download_btn.clicked.connect(self.on_download_clicked)
        self.plus_btn.clicked.connect(self.on_plus_btn_clicked)
        self.minus_btn.clicked.connect(self.on_minus_btn_clicked)
        self.rename_btn.clicked.connect(self.on_rename_btn_clicked)
        self.apply_btn.clicked.connect(self.on_apply_btn_clicked)
        self.reset_btn.clicked.connect(self.on_reset_btn_clicked)

    def download_base(self):
        self.renew_tree('remote', self.db_control.get_remote_storage())

    def renew_tree(self, tree, data=None):
        if tree == 'local':
            treeview = self.local_tree
        elif tree == 'remote':
            treeview = self.remote_tree
        else:
            self.local_tree.clear()
            self.remote_tree.clear()
            return 0

        self.tree_storage = dict()
        treeview.clear()
        self.make_items(treeview, data)

    def make_items(self, tree, data):
        for item_id, item_raw in data.items():
            self.make_qitem(item_raw, tree, data)

    def make_qitem(self, item_raw, tree, data):
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
        if tree == 'remote':
            item = self.remote_tree.currentItem()
        else:
            item = self.local_tree.currentItem()
        if item:
            return item.text(1)
        else:
            return None

    def get_current_name(self):
        item = self.local_tree.currentItem()
        if item:
            return item.text(0)
        else:
            return None

    def get_current_value(self):
        item = self.local_tree.currentItem()
        if item:
            return item.text(2)
        else:
            return None

    def on_download_clicked(self):
        if self.get_current_id(tree='remote'):
            tree, data = self.db_control.pull(self.get_current_id(tree='remote'))
            self.renew_tree(tree, data)

    def on_plus_btn_clicked(self):
        tree, data = self.db_control.add_item({'parent': self.get_current_id(tree='local')})
        self.renew_tree(tree, data)

    def on_minus_btn_clicked(self):
        tree, data = self.db_control.del_item(self.get_current_id(tree='local'))
        self.renew_tree(tree, data)

    def on_rename_btn_clicked(self):
        if self.get_current_id(tree='local'):
            self.download_btn.setEnabled(False)
            self.dlg = self.show_dialog()
            self.dlg.resultOk.connect(self.send_changes)

    def on_apply_btn_clicked(self):
        tree, data = self.db_control.commit()
        self.renew_tree(tree, data)
        self.download_btn.setEnabled(True)

    def on_reset_btn_clicked(self):
        self.renew_tree(self.db_control.reset())
        self.download_base()

    def show_dialog(self):
        default_name = self.get_current_name()
        default_val = self.get_current_value()

        dia = NameValDialog(default_name, default_val)

        return dia

    def send_changes(self, name, value):
        item_id = self.get_current_id(tree='local')
        tree, data = self.db_control.change_item(item_id, name=name, value=value)
        self.renew_tree(tree, data)
