from structures.db import Database
from structures.sprint import Sprint

class Task:

    def __init__(self, type, time, object, object_id):

        self.__db = Database.instance()
        self.type = type
        self.time = time
        self.object = object
        self.object_id = object_id

    def get(self):
        """
        Check to see if a task of this type and object_id already exists
        :return:
        """
        return self.__db.get('tasks', {'type' : self.type, 'object': self.object, 'objectid': self.object_id})

    def schedule(self):
        """
        Schedule the task in the database
        :return:
        """

        # If this task already exists, just update its time.
        record = self.get()
        if record:
            return self.__db.update('tasks', {'time': self.time}, {'id': record['id']})

        # Otherwise, create one.
        else:
            return self.__db.insert('tasks', {'type': self.type, 'time': self.time, 'object': self.object, 'objectid': self.object_id})

    def run(self):
        """
        Run this task
        :return:
        """
        if self.object == 'sprint':
            method = 'task_' + str(self.type)
            # getattr(Sprint, method)()
        else:
            raise Exception('Invalid task object: ' + str(self.object))

    def cancel(object, object_id, type=None):
        """
        Cancel all tasks related to a specific object
        :param object:
        :param object_id:
        :return:
        """
        db = Database.instance()

        params = {'object': object, 'objectid': object_id}
        if type is not None:
            params['type'] = type

        return db.delete('tasks', params)