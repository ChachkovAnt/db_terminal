import json
from copy import copy
from random import randint


class Node:
    """
    Class Node describes the simplest entity in tree.
    """
    def __init__(self, kwargs):
        """
        Node initializes using kwarg dictionary. It means that you need to pass argument like this:
        {'parent' = '3'}, !!!! not like (parent='3') !!!!

        Node have 6 attributes:
        Name - name of node. It is a volatile cell, can be changed by user.
        Value - string value. It is a volatile cell, can be changed by user.
        Id - identificator which must be unique in base.
        Parent - contents id of parent. It can not be changed or deleted. If parent None -> node is root.
        Children - contents list of children. By default it is a empty list if children didn't set from the outside.
        """
        self.deleted = True if self.parse_arg('deleted', kwargs) else False

        self.id = str(self.parse_arg('id', kwargs))
        self.parent = str(self.parse_arg('parent', kwargs))
        self.children = self.parse_arg('children', kwargs)

        self.name = str(self.set_name(self.parse_arg('name', kwargs)))
        self.value = str(self.parse_arg('value', kwargs))

    def print_node(self):
        """
        It used for printing node content in stdout just for debugging model.
        :return: None
        """
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
        """
        Setting value. If value did not passed, empty string sets to.
        :param value: str
        :return: None
        """
        if not self.deleted:
            self.value = value if value else ''

    def set_name(self, name):
        """
        Name setter. If name did not passed, 'default_nameNUM' sets to.
        :param name: str
        :return: name
        """
        default_name = 'default_name' + self.id
        self.name = name if name else default_name
        return self.name

    def set_child(self, child):
        """
        Appends child in children list
        :param child: str
        :return: None
        """
        self.children.append(child)

    def del_node(self):
        """
        Make current item deleted.
        :return: None
        """
        self.deleted = True

    def pack_raw(self, is_copy=True, parent=None, new_id=None):
        """
        Casting Node object to dict(). It used to make a local copy of remote node or transmit between bases. If you
        need to really transmit it to socket for ex., you can simply create json and transmit it where you need.

        :param is_copy: True - if it used for make copy.
        :param parent: if parent did not passed, sets parent from self.parent.
        :param new_id: if id did not passed, sets id from self.id.
        :return: raw_node - item in dictionary format, where attributes
        """
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
    """
    Class DBStorage describes local cache.
    """
    def __init__(self):
        self.storage = dict()

    def add_item(self, item):
        """
        Adding item into local cache.
        :param item: Node class.
        :return: None
        """
        self.find_relatives(self.storage, item)             # Search relatives
        self.storage[item.id] = item                        # Add in storage with new relatives

        if self.storage.get(item.parent):                   # Check for deleted parent.
            if self.storage[item.parent].deleted:
                self.del_item(item.id)                      # Delete myself and delete all my children

        if item.deleted:
            self.del_item(item.id)

    def del_item(self, item_id):
        """
        Making delete itself and all of its children.
        :param item_id: id of item, which must be deleted
        :return: None
        """
        if item_id in self.storage:
            self.storage[item_id].del_node()
            for child_id in self.storage[item_id].children:
                self.del_item(child_id)

    @staticmethod
    def find_relatives(storage, item):
        """
        Finds parent and all the children in storage for item.
        :param storage: dict()
        :param item: Node()
        :return: None
        """
        if item.parent in storage.keys() and item.id not in storage[item.parent].children:
            storage[item.parent].set_child(item.id)

        for item_id, item_node in storage.items():
            if item_node.parent == item.id and item_id not in item.children:
                item.set_child(item_node.id)

    def print_cache(self):
        """
        Prints all nodes in stdout
        """
        for key in self.storage:
            self.storage[key].print_node()

    def change_item_volatile(self, item_id, **kwargs):
        """
        Changes item's name and value or sets their defaults. It is no action, if node has been deleted.
        :param item_id: str
        :param kwargs: key-val pair like: name='name', value='value'
        :return: None
        """
        if not self.storage[item_id].deleted:
            if 'name' in kwargs:
                self.storage[item_id].set_name(str(kwargs['name']))

            if 'value' in kwargs:
                self.storage[item_id].set_value(str(kwargs['value']))
        else:
            return

    def get_item(self, item_id):
        """
        Gets Node in dict() format with children.
        :param item_id: str item_id
        :return: dict(Node)
        """
        return self.storage[str(item_id)].pack_raw(is_copy=False)

    def receive_item(self, item):
        """
        :param item: dict() raw_node
        :return: None
        """
        self.add_item(item)

    def reset(self):
        """
        Resets cache
        :return: None
        """
        self.__init__()

    def __iter__(self):
        return ((id, item.pack_raw(is_copy=False)) for (id, item) in self.storage.items())


class RemoteDB(DBStorage):
    """
    Class RemoteDB inherits from DBStorage, because their behavior are similar.
    """
    def __init__(self):
        """
        Inits as like superclass and then loads default database from .txt file.
        """
        DBStorage.__init__(self)
        self.parse_json()

    def parse_json(self):
        """
        Loads default database from file "db.txt"
        :return: None
        """
        with open('database//db.txt', 'r') as db:
            raw_dict = json.loads(db.read())
            for key, val in raw_dict.items():
                node = Node(val)
                self.add_item(node)


class DBManager:
    """
    Class DBManager describes relations between local cache and remote database
    """
    def __init__(self):
        """
        Inits DBStorage and RemoteDB instances. Makes ID generator for randomize new ids.
        """
        super().__init__()
        self.local_storage = DBStorage()
        self.remote_storage = RemoteDB()
        self.gen = self.id_gen()

    def pull(self, item_id):
        """
        One-by-one download implementation
        :param item_id: str
        :return: 'local', storage
        """
        item = Node(self.remote_storage.get_item(item_id))
        self.local_storage.receive_item(item)
        return 'local', self.get_local_storage()

    def commit(self):
        """
        Pushes and updates to remote database all cached items.
        :return: 'remote', storage
        """
        for item_id, item in self.local_storage.storage.items():
            self.remote_storage.receive_item(copy(item))
        self.renew_local()  # Renew local tree after commit

        return 'remote', self.get_remote_storage()

    def add_item(self, item_raw):
        """
        Adds new item in cache. Must be called by user through the UI.
        :param item_raw: dict(Node)
        :return: 'local', storage
        """
        parent = self.local_storage.storage.get(item_raw['parent'])  # Get the parent
        is_par_del = parent.deleted if parent else False             # Write parent check expression in var

        if not is_par_del:                      # If parent hasn't been deleted add new node
            item_raw['id'] = next(self.gen)
            item = Node(item_raw)
            self.local_storage.add_item(item)
        return 'local', self.get_local_storage()

    def renew_local(self):
        """
        Renew local tree when commit changes in remote tree
        :return: None
        """
        store = self.remote_storage.storage
        for item_id, item_raw in self.local_storage:
            if item_id in store:
                self.pull(item_id)

    def change_item(self, item_id, **kwargs):
        """
        Changes item's volitile values(Name/Value). Must be called by user through the UI.
        :param item_id: str
        :param kwargs: pairs of params: name='name', value='value'
        :return: 'local', storage
        """
        self.local_storage.change_item_volatile(item_id, **kwargs)
        return 'local', self.get_local_storage()

    def del_item(self, item_id):
        """
        Makes item deleted. Must be called by user through the UI.
        :param item_id: str
        :return: 'local', tree
        """
        self.local_storage.del_item(str(item_id))
        return 'local', self.get_local_storage()

    def id_gen(self):
        """
        Random ID generator. Generation range from 0 to 65535.
        :return: id
        """
        while True:
            idg = randint(0, 0xffff)
            if str(idg) not in self.remote_storage.storage.keys():
                yield str(idg)

    def reset(self):
        """
        Resets views and bases. Must be called by user through the UI.
        :return: 'all' (command for reset treeViews)
        """
        self.remote_storage.reset()
        self.local_storage.reset()
        return 'all'

    def get_local_item(self, item_id):
        return self.local_storage.get_item(item_id)

    def get_remote_storage(self):
        return dict(self.remote_storage)

    def get_local_storage(self):
        return dict(self.local_storage)

    def is_deleted(self, item_id, store='local'):
        """
        Is deleted check.
        :param item_id: str
        :param store: 'local' or 'remote'
        :return: bool (deleted --> True)
        """
        if store == 'local':
            deleted = self.local_storage.storage[item_id].deleted
        else:
            deleted = self.remote_storage.storage[item_id].deleted

        return deleted

