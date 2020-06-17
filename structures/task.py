import time
from structures.db import Database

from pprint import pprint

class Task:

    def __init__(self, id):
        """
        Load a Task object by its ID
        :param id:
        """
        self.__db = Database.instance()
        self.id = None

        record = self.__db.get('tasks', {'id': id})
        if record:
            self.id = record['id']
            self.type = record['type']
            self.time = record['time']
            self.object = record['object']
            self.object_id = record['objectid']
            self.processing = record['processing']

    def is_valid(self):
        """
        Check if the Task object is valid
        :return:
        """
        return self.id is not None

    def is_processing(self):
        """
        Check if this task is already running
        :return:
        """
        return self.processing == 1

    def start_processing(self, value):
        """
        Mark the task as processing or not
        :param value: 0 or 1
        :return:
        """
        return self.__db.update('tasks', {'processing': value}, {'id': self.id})

    async def run(self, bot):
        """
        Run this task
        TODO: In the future, make this better. For now it will do.
        :return: bool
        """

        # If the task is already processing, don't go any further.
        if self.is_processing():
            return True

        # Mark the task as processing so other shards don't pick it up.
        self.start_processing(1)

        result = False

        # Sprint tasks.
        if self.object == 'sprint':

            from structures.sprint import Sprint

            sprint = Sprint.get(self.object_id)
            if sprint.is_valid():
                method = 'task_' + str(self.type)
                result = await getattr(sprint, method)(bot, self)
            else:
                # If the sprint doesn't exist, then we can just delete this task.
                result = True

        else:
            # Invalid task object. May as well just delete this task.
            print('Invalid task object: ' + self.object)
            result = True

        # The task might have to run several times, as there are multiple shards and the first one to run it might not be able to get_channel() on the channel id.
        # So we only want to delete the task from the database if it explicitly returns True.
        if result is True:
            self.delete()
        else:
            self.start_processing(0)

        return result

    def delete(self):
        """
        Delete the task
        :return:
        """
        return self.__db.delete('tasks', {'id': self.id})

    async def execute_all(bot):
        """
        Execute a pass of the scheduled tasks that are currently pending
        :return:
        """
        now = int(time.time())
        db = Database.instance()

        pending = db.get_all_sql('SELECT id FROM tasks WHERE time <= %s ORDER BY id ASC', [now])
        for row in pending:
            task = Task(row['id'])
            if task.is_valid():
                result = await task.run(bot)

    def cancel(object, object_id, type=None):
        """
        Cancel all tasks related to a specific object
        :param object:
        :param object_id:
        :param type:
        :return:
        """
        db = Database.instance()

        params = {'object': object, 'objectid': object_id}
        if type is not None:
            params['type'] = type

        return db.delete('tasks', params)

    def get(type, object, object_id):
        """
        Check to see if a task of this type and object_id already exists
        :return:
        """
        db = Database.instance()
        return db.get('tasks', {'type' : type, 'object': object, 'objectid': object_id})

    def schedule(type, time, object, object_id):
        """
        Schedule the task in the database
        :return:
        """
        db = Database.instance()

        # If this task already exists, just update its time.
        record = Task.get(type, object, object_id)
        if record:
            return db.update('tasks', {'time': time}, {'id': record['id']})
        else:
            # Otherwise, create one.
            return db.insert('tasks', {'type': type, 'time': time, 'object': object, 'objectid': object_id})