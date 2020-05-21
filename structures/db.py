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

    def get(self, table, where=None, fields=['*']):
        self.__build_get(table, where, fields)
        return self.cursor.fetchone()

    def getall(self, table, where=None, fields=['*']):
        self.__build_get(table, where, fields)
        return self.cursor.fetchall()