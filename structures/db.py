import sys, os, lib, pymysql, warnings
from structures.singleton import Singleton

# sys.path.append(os.path.abspath('../'))

@Singleton
class Database:

    # Create database connection
    def __init__(self):

        self.__path = os.path.abspath(os.path.dirname(__file__))

        # Load the connection configuration
        config = lib.get(self.__path + '/../settings.json')
        self.connection = pymysql.connect(host=config.db_host, user=config.db_user, passwd=config.db_pass, db=config.db_name, autocommit=True)

        # Set the cursor to be used, with DictCursor so we can refer to results by their keys
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    # Close connection on destruction of object
    def __del__(self):
        self.connection.close()

    def install(self):

        install_path = self.__path + '/../data/install/'

        try:

            for filename in os.listdir(install_path):

                file = open(os.path.join(install_path, filename), 'r')
                sql = file.read()

                # Suppress warnings about the tables already existing
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    self.cursor.execute(sql)

        except:
            self.connection.rollback()
            raise

        else:
            self.connection.commit()
            return True

    def __build_get(self, table, where=None, fields=['*']):

        params = []

        sql = 'SELECT ' + ', '.join(fields) + ' ' \
              'FROM ' + table + ' '

        if where is not None:

            sql += 'WHERE '

            for field, value in where.items():
                sql += field + ' = %s AND '
                params.append(value)

            # Remove the last 'AND '
            sql = sql[:-4]

        self.cursor.execute(sql, params)

    def __build_insert(self, table, params):

        # Create param placeholders to be used in the query
        placeholders = ['%s'] * len(params.values())

        sql = 'INSERT INTO ' + table + ' '
        sql += '(' + ','.join(params.keys()) + ') '
        sql += 'VALUES '
        sql += '(' + ','.join(placeholders) + ') '

        sql_params = list(params.values())
        self.cursor.execute(sql, sql_params)

    def __build_delete(self, table, params):

        sql_params = []
        sql = 'DELETE FROM ' + table + ' WHERE '

        for field, value in params.items():
            sql += field + ' = %s AND '
            sql_params.append(value)

        # Remove the last 'AND '
        sql = sql[:-4]

        # Execute the query
        self.cursor.execute(sql, sql_params)

    def __build_update(self, table, params, where):

        sql_params = []
        sql = 'UPDATE ' + table + ' SET '

        # Set values
        for field, value in params.items():
            sql += field + ' = %s, '
            sql_params.append(value)

        # Remove the last ', '
        sql = sql[:-2]

        # Where clauses
        sql += ' WHERE '

        for field, value in where.items():
            sql += field + ' = %s AND '
            sql_params.append(value)

        # Remove the last 'AND '
        sql = sql[:-4]

        # Execute the query
        self.cursor.execute(sql, sql_params)

    def get(self, table, where=None, fields=['*']):
        self.__build_get(table, where, fields)
        return self.cursor.fetchone()

    def get_all(self, table, where=None, fields=['*']):
        self.__build_get(table, where, fields)
        return self.cursor.fetchall()

    def insert(self, table, params):
        self.__build_insert(table, params)
        return self.cursor.rowcount

    def delete(self, table, params):
        self.__build_delete(table, params)
        return self.cursor.rowcount

    def update(self, table, params, where):
        self.__build_update(table, params, where)
        return self.cursor.rowcount