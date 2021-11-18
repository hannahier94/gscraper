import psycopg2
import os
from utils import fetch_json

DATABASE_URL = os.environ['DATABASE_URL']

class DbBuild:

    CREATE_TABLE_STATEMENT = '''CREATE TABLE if not exists classifier ( \
                                 url TEXT PRIMARY KEY, \
                                 search_string TEXT,
                                 classification INTEGER,
                                 class_name TEXT);'''

    INSERT_STATEMENT = """INSERT INTO classifier(url, search_string, classification, class_name)
                            VALUES(%s, %s, %s, %s);"""

    SELECT_STATEMENT = """SELECT count(url) from classifier WHERE url = %s ;"""

    SEARCH_STRING_SELECT_STATEMENT =  """SELECT count(url) from classifier WHERE search_string = %s ;"""

    def __init__(self):
        self._create_connection()
        self._cursor = self._conn.cursor()
        self._create_table()


    def _check_single_record(self, single_url):
        single_url = (single_url,)
        self._cursor.execute(self.SELECT_STATEMENT, single_url)
        count = self._cursor.fetchone()[0]
        if count != 0:
            return True
        else:
            return False

    def check_urls(self, initial_results, limit=5):
        filtered_results = []
        for res in initial_results:
            if len(filtered_results) >= limit:
                break
            if self._check_single_record(res["link"]):
                continue
            else:
                filtered_results.append(res)
        self.close_conn()
        return filtered_results

    def _create_connection(self):
        #establishing the connection
        self._conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    def _create_table(self):
        self._cursor.execute(self.CREATE_TABLE_STATEMENT)
        self._conn.commit()
        print("** Table created successfully **")

    def close_conn(self):
        self._conn.close()

    def check_previous_searches(self, search_string):
        search_string = (search_string,)
        self._cursor.execute(self.SEARCH_STRING_SELECT_STATEMENT, search_string)
        count = self._cursor.fetchone()[0]
        self.close_conn()
        return count

    def write_lines(self, classifications, search_string):
        TOKEN_KEY = "csrf_token"

        results = fetch_json("results.json")
        labels_mapper = fetch_json("utils_vars.json")["buttons_vals"]

        for key, val in classifications.items():
            if key == TOKEN_KEY:
                continue
            ind = int(key.split('_')[1])
            link = results[ind]['link']
            val_label = next((button["button_id"] for button in labels_mapper
                              if int(button["value"]) == int(val)), "unknown_value")
            records = (link, search_string, val, val_label)
            self._cursor.execute(self.INSERT_STATEMENT, records)
        self._conn.commit()
        self.close_conn()
        print('** Records inserted successfully **')


