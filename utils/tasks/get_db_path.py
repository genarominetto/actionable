from kivy.utils import platform
import os
import sqlite3

def get_db_path(db_name):
    if platform == 'android':
        from android.storage import app_storage_path
        data_dir = app_storage_path()
    else:
        data_dir = os.getcwd()

    return os.path.join(data_dir, db_name)
