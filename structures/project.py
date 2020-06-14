import lib
from structures.db import Database

class Project:

    def __init__(self, id):

        self.__db = Database.instance()

        record = self.__db.get('projects', {'id': id})
        if record:
            self._id = record['id']
            self._user = record['user']
            self._name = record['name']
            self._shortname = record['shortname']
            self._words = record['words']
            self._completed = record['completed']

    def get_id(self):
        return self._id

    def get_user(self):
        return self._user

    def get_name(self):
        return self._name

    def get_title(self):
        return self.get_name()

    def get_shortname(self):
        return self._shortname

    def get_words(self):
        return self._words

    def is_completed(self):
        return int(self._completed) == 1

    def delete(self):
        """
        Delete the project
        :return:
        """
        return self.__db.delete('projects', {'id': self._id})

    def get(user, shortname):
        """
        Try to get a project with a given shortname, for a given user
        :param user:
        :param shortname:
        :return:
        """
        db = Database.instance()
        record = db.get('projects', {'user': user, 'shortname': shortname})
        return Project(record['id']) if record else None


    def create(user, shortname, name):
        """
        Create a new project
        :param name:
        :return:
        """
        db = Database.instance()
        return db.insert('projects', {'user': user, 'shortname': shortname, 'name': name})