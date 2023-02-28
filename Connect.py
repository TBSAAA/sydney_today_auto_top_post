import pymysql
import local_settings
from pymysql.cursors import DictCursor


class Connect(object):
    def __init__(self):
        self.conn = conn = pymysql.connect(**local_settings.MYSQL_CONN_PARAMS)
        self.cursor = conn.cursor(pymysql.cursors.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def fetch_one(self, sql, **kwargs):
        try:
            self.cursor.execute(sql, kwargs)
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(e)
            return None

    def fetch_all(self, sql, **kwargs):
        try:
            self.cursor.execute(sql, kwargs)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
            return None

    def execute(self, sql, **kwargs):
        try:
            self.cursor.execute(sql, kwargs)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False

    def execute_many(self, sql, args):
        try:
            self.cursor.executemany(sql, args)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
            return False