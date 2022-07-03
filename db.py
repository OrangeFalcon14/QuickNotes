import sqlite3 as sql
from datetime import datetime
import os
from pathlib import Path
import platform

home_dir = os.environ["HOME"]

if platform.system() == "Linux" or platform.system() == "Darwin":
    db_path = home_dir + ".config/quicknotes/notes.db"

if platform.system() == "Windows":
    db_path = home_dir + ".quicknotes/notes.db"

connection = sql.Connection(db_path)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS notes (date TEXT, time TEXT, title TEXT, note_text TEXT, id INTEGER)")


def get_notes():
    return cursor.execute("SELECT * FROM notes").fetchall()


def write_new_note(title, note_text):
    date = datetime.now().date()
    time = str(datetime.now().hour) + ":" + str(datetime.now().minute)

    titles = cursor.execute("SELECT title FROM notes").fetchall()
    temp = []
    for x in titles:
        temp.append(x[0])
    titles = temp.copy()
    del temp
    if title not in titles and title.strip() != "":
        cursor.execute("INSERT INTO notes (date, time, title, note_text) VALUES (?,?,?,?)", [date, time, title, note_text])
        connection.commit()
    else:
        if title in titles:
            raise Exception("A note by that name already exists.")
        else:
            raise Exception("Title must not be empty.")


def update_db(note, title, note_text):
    if title.strip() != "":
        try:
            sql_statement = f"""UPDATE notes 
                            SET title = '{title}', note_text = '{note_text}'
                            WHERE rowid = '{note[-1]}'
                            """
            cursor.execute(sql_statement)
            connection.commit()
        except Exception as e:
            raise e
    else:
        raise Exception("Title must not be empty")


def delete_record(index):
    try:
        sql_statement = f"""DELETE FROM notes WHERE id = {index}"""
        cursor.execute(sql_statement)
        connection.commit()
    except Exception as e:
        raise e


def write_new_note_numbers():
    for x in range(len(get_notes()) + 1):
        try:
            title = get_notes()[x - 1][2]
            sql_statement = f"""UPDATE NOTES
                                SET id = {x}
                                WHERE title = '{title}'"""
            cursor.execute(sql_statement)
        except Exception as e:
            # title = get_notes()[0][2]
            pass
