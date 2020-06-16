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

    def complete(self, value=1):
        """
        Mark the project as complete
        :return:
        """
        self._completed = value
        return self.__db.update('projects', {'completed': value}, {'id': self._id})

    def uncomplete(self):
        """
        Mark a project as NOT completed
        :return:
        """
        # We mark it as -1 instead of 0, so we don't award them XP for completing it again in the future.
        return self.complete(-1)

    def add_words(self, amount):
        """
        Add words to the word count
        :param amount:
        :return:
        """
        self._words += int(amount)
        return self.__db.update('projects', {'words': self._words}, {'id': self._id})

    def update(self, amount):
        """
        Update the word count of the project
        :param amount:
        :return:
        """
        self._words = amount
        return self.__db.update('projects', {'words': amount}, {'id': self._id})

    def rename(self, shortname, name):
        """
        Rename a project
        :param shortname:
        :param name:
        :return:
        """
        self._shortname = shortname
        self._name = name
        return self.__db.update('projects', {'shortname': shortname, 'name': name}, {'id': self._id})

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

    def all(user):
        """
        Get an array of Projects for a given user
        :param user:
        :return:
        """
        db = Database.instance()
        records = db.get_all('projects', {'user': user}, ['id'], ['completed', 'name', 'shortname', 'words'])
        projects = []

        for record in records:
            projects.append(Project(record['id']))

        return projects

    def create(user, shortname, name):
        """
        Create a new project
        :param name:
        :return:
        """
        db = Database.instance()
        return db.insert('projects', {'user': user, 'shortname': shortname, 'name': name})