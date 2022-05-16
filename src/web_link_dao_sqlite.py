import sqlite3
from typing import List

from src.web_link import WebLink
from src.web_link_dao import WebLinkDAO


class WebLinkDAOSQLite(WebLinkDAO):
    def __int__(self):
        self.connector = None

    def _table_exists(self, name: str):
        c = self.connector.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}' '''.format(name))
        return c.fetchone()[0] == 1

    def _create_weblink_table(self):
        c = self.connector.cursor()
        c.execute('''   CREATE TABLE WEBLINK (
                        URL TEXT PRIMARY KEY,
                        PARENT TEXT,
                        VISITED INTEGER NOT NULL DEFAULT 0,
                        ERROR INTEGER DEFAULT 0
                        ); ''')
        self.connector.commit()

    def set_up(self):
        self.connector = sqlite3.connect('./wlinks.db')
        if not self._table_exists('WEBLINK'):
            self._create_weblink_table()

    def get_unvisited_links(self, n: int = 0):
        c = self.connector.cursor()
        query = 'SELECT * FROM WEBLINK WHERE VISITED=FALSE'
        if n > 0:
            query += ' LIMIT {}'.format(n)
        c.execute(query)
        return [self._tuple_to_wl(ln) for ln in c]

    def save_update_links(self, links: List[WebLink]):
        for ln in links:
            if self.has_link_with_url(ln.url):
                self.update_link(ln)
            else:
                self.save_link(ln)

    def save_link(self, link: WebLink):
        c = self.connector.cursor()
        visited, error, parent = self._get_sql_parameters(link)
        c.execute('''   INSERT INTO WEBLINK (
                        URL, PARENT, VISITED, ERROR)
                        VALUES (
                        "{}", {}, {}, {}); '''.format(link.url, parent, visited, error))
        self.connector.commit()

    def update_link(self, link: WebLink):
        c = self.connector.cursor()
        visited, error, parent = self._get_sql_parameters(link)
        c.execute('''   UPDATE WEBLINK SET
                        PARENT={}, VISITED={}, ERROR={}
                        WHERE URL="{}"'''.format(parent, visited, error, link.url))
        self.connector.commit()

    @staticmethod
    def _get_sql_parameters(link: WebLink):
        visited = 1 if link.visited else 0
        error = 1 if link.error else 0
        parent = '"{}"'.format(link.parent) if link.parent else 'NULL'
        return visited, error, parent

    def has_link_with_url(self, url: str) -> bool:
        c = self.connector.cursor()
        c.execute('''SELECT COUNT(URL) FROM WEBLINK WHERE URL="{}"'''.format(url))
        return c.fetchone()[0] == 1

    @staticmethod
    def _tuple_to_wl(database_tuple):
        url, parent, visited, error = database_tuple
        parent = None if parent == 'NULL' else parent
        visited = True if visited == 1 else False
        error = True if error == 1 else False
        return WebLink(url, parent, visited, error)

    def set_visited(self, url: str, value: bool):
        self._set_int_attribute(url, 'VISITED', 1 if value else 0)

    def set_error(self, url: str, value: bool):
        self._set_int_attribute(url, 'ERROR', 1 if value else 0)

    def _set_int_attribute(self, url: str, attribute_name: str, value: int):
        c = self.connector.cursor()
        c.execute('''UPDATE WEBLINK SET {}={} WHERE URL="{}"'''.format(attribute_name, value, url))
        self.connector.commit()
