import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


class UseDataBase():

    configuration = {'host': 'mysql.92oopss.myjino.ru',
                     'user': '92oopss',
                     'password': '9python9',
                     'database': '92oopss',}

    def create_connection(self):
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor          
        
    def query_insert(self, *args):
        self.cursor.execute(*args)

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


class UsePoolConnectionToDB():

    configuration = {'host': 'mysql.92oopss.myjino.ru',
                     'user': '92oopss',
                     'password': '9python9',
                     'database': '92oopss',}

    def __init__(self, name, size):
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name = name,
                                                                   pool_size = size,
                                                                   **self.configuration)

    def create_cursor(self):
        self.cnx = self.cnxpool.get_connection()
        self.cursor = self.cnx.cursor()
        return self.cursor

    def query_insert(self, *args):
        self.cursor.execute(*args)

    def close(self):
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
