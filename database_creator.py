import mysql.connector
from mysql.connector import errorcode

dbconfig = {'host': 'localhost',
            'user': 'root',
            'password': '',}

DB_NAME = 'parserDB'

TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "`id` INT(11) AUTO_INCREMENT PRIMARY KEY,"
    "`username` longtext NOT NULL,"
    "`password` longtext NOT NULL"
    ")")

TABLES['parse'] = (
    "CREATE TABLE `parse` ("
    "`id` INT(11) AUTO_INCREMENT PRIMARY KEY,"
    "`title` longtext NOT NULL,"
    "`price` longtext NOT NULL,"
    "`time` longtext NOT NULL,"
    "`place` longtext NOT NULL,"
    "`phone` longtext NOT NULL,"
    "`url` longtext NOT NULL"
")")

cnx = mysql.connector.connect(**dbconfig)
cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    try:
        cursor.execute("INSERT INTO users(username, password) VALUES ('admin', 'root')")
    except:
        pass
        
    cnx.commit()
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    create_database(cursor)