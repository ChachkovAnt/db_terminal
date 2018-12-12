import json
from copy import copy
from random import randint
from PyQt5.QtCore import pyqtSignal, QObject


# Create node class
class Node:

    def __init__(self, kwargs):

        self.deleted = True if self.parse_arg('deleted', kwargs) else False

        self.id = str(self.parse_arg('id', kwargs))
        self.parent = str(self.parse_arg('parent', kwargs))
        self.children = self.parse_arg('children', kwargs)

        self.name = str(self.set_name(self.parse_arg('name', kwargs)))
        self.value = str(self.parse_arg('value', kwargs))

    def print_node(self):
        if not self.deleted:
            print('id{}:'.format(self.id))
            print('\tname = {}'.format(self.name))
            print('\tvalue = {}'.format(self.value))
            print('\tparent = {}'.format(self.parent))
            print('\tchildren = {}'.format(self.children))
            print('\tdeleted = {}'.format(self.deleted))
        else:
            print('Node id{} is deleted'.format(self.id))

    @staticmethod
    def parse_arg(name, kwargs):
        if name in kwargs.keys():
            return kwargs.get(name)
        elif name == 'children':
            return []

    def set_value(self, value):
        if not self.deleted:
            self.value = value if value else ''

    def set_name(self, name):
        default_name = 'default_name' + self.id
        self.name = name if name else default_name
        return self.name

    def set_child(self, child):
        self.children.append(child)

    def del_node(self):
        self.deleted = True

    # Можно объявить статик методом и создавать новый дефолтный узел
    # По умолчанию мы генерируем узел для копии, однако так же можем
    # сгенерировать новый узел в локальном кэше
    def pack_raw(self, is_copy=True, parent=None, new_id=None):
        raw_node = dict()
        raw_node['id'] = str(new_id) if new_id else self.id
        raw_node['parent'] = parent if parent else self.parent
        raw_node['name'] = self.name
        raw_node['value'] = self.value
        raw_node['deleted'] = self.deleted
        if not is_copy:
            raw_node['children'] = self.children
        else:
            raw_node['children'] = []

        return raw_node

    def __copy__(self):
        return Node(self.pack_raw(is_copy=True))


class DBStorage:

    def __init__(self):
        self.storage = dict()

    def add_item(self, item):
        if self.storage.get(item.parent):
            if self.storage[item.parent].deleted:
                return

        self.find_relatives(self.storage, item)
        if self.storage.get(item.id):
            item.deleted = self.storage[item.id].deleted

        self.storage[item.id] = item

    def del_item(self, item_id):
        if item_id in self.storage:
            self.storage[item_id].del_node()
            for child_id in self.storage[item_id].children:
                self.del_item(child_id)

    @staticmethod
    def find_relatives(storage, item):
        """
            find_relatives(storage, item) находит всех родителей и детей в storage для item
        """
        if item.parent in storage.keys() and item.id not in storage[item.parent].children:
            storage[item.parent].set_child(item.id)

        # Ищем детей перебором по всему кэшу, если находим, добаляем в свой список детей
        for item_id, item_node in storage.items():
            if item_node.parent == item.id and item_id not in item.children:
                item.set_child(item_node.id)

    def print_cache(self):
        """
        print_cache() выводит все сождержимое базы в stdout
        """
        for key in self.storage:
            self.storage[key].print_node()

    def change_item_volatile(self, item_id, **kwargs):
        if not self.storage[item_id].deleted:
            if 'name' in kwargs:
                self.storage[item_id].set_name(str(kwargs['name']))

            if 'value' in kwargs:
                self.storage[item_id].set_value(str(kwargs['value']))
        else:
            return

    def get_item(self, item_id):
        return self.storage[str(item_id)].pack_raw(is_copy=False)

    def receive_item(self, item):
        self.add_item(item)

    def reset(self):
        self.__init__()

    def __iter__(self):
        return ((id, item.pack_raw(is_copy=False)) for (id, item) in self.storage.items())


# Унаследуем класс DBStorage, для реализации удаленной базы данных
class RemoteDB(DBStorage):
    def __init__(self):
        DBStorage.__init__(self)
        self.parse_json()

    def parse_json(self):
        with open('db.txt', 'r') as db:
            raw_dict = json.loads(db.read())
            for key, val in raw_dict.items():
                node = Node(val)
                self.add_item(node)

    def add_item(self, item):
        if self.storage.get(item.parent):
            if self.storage[item.parent].deleted:
                item.deleted = True

        self.find_relatives(self.storage, item)
        self.storage[item.id] = item
        if item.deleted:
            self.del_item(item.id)


# Создадим класс менеджера данных, который будет скачивать и сливать данные из баз.
class DBManager(QObject):

    treeChanged = pyqtSignal(str, dict)

    # Затолкаем внутрь локальный кэш
    def __init__(self):
        super().__init__()
        self.local_storage = DBStorage()
        self.remote_storage = RemoteDB()
        self.gen = self.id_gen()

    # Реализация выкачивания из удаленной базы по одному элементу
    def pull(self, item_id):
        self.local_storage.receive_item(Node(self.remote_storage.get_item(item_id)))
        return 'local', self.get_local_storage()

    # Реализация слияния локального кэша и удаленной базы
    def commit(self):
        for item_id, item in self.local_storage.storage.items():
            self.remote_storage.receive_item(copy(item))
        return 'remote', self.get_remote_storage()

    def add_item(self, item):
        item['id'] = next(self.gen)
        item = Node(item)
        self.local_storage.add_item(item)
        return 'local', self.get_local_storage()

    def change_item(self, item_id, **kwargs):
        self.local_storage.change_item_volatile(item_id, **kwargs)
        # self.treeChanged.emit('local', self.get_local_storage())
        return 'local', self.get_local_storage()

    def del_item(self, item_id):
        self.local_storage.del_item(str(item_id))
        # self.treeChanged.emit('local', self.get_local_storage())
        return 'local', self.get_local_storage()

    def id_gen(self):
        while True:
            idg = randint(0, 0xffff)
            if str(idg) not in self.remote_storage.storage.keys():
                yield str(idg)

    def reset(self):
        self.remote_storage.reset()
        self.local_storage.reset()
        return 'all'

    def get_local_item(self, item_id):
        return self.local_storage.get_item(item_id)

    def get_remote_storage(self):
        return dict(self.remote_storage)

    def get_local_storage(self):
        return dict(self.local_storage)
