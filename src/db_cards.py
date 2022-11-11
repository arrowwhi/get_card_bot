import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"connect The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"execute The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"read The error '{e}' occurred")


def add_value(path, name, desc):
    add_card = """
INSERT INTO cards (path, name, description)
VALUES ('""" + path + """', '""" + name + """', '""" + desc + """');
    """
    return add_card


def return_all():
    q = """
    SELECT path from cards
    """
    return q


def create_table():
    q = """
    CREATE TABLE IF NOT EXISTS cards (
        card_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT );
    """
    return q


def rows_rows():
    q = """
    SELECT COUNT(*) from cards
    """
    return q


def get_photo_id(number):
    q = """
    SELECT name,path from cards
    WHERE card_id=""" + str(number)
    return q


def get_all_photo_paths():
    q = """
    SELECT path, name from cards
    """
    return q


def get_all_photo_names_ids():
    q = """
    SELECT card_id, name from cards
    """
    return q


def delete_value(num):
    q = "DELETE FROM cards WHERE card_id = " + str(num)
    return q
