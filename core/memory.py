import sqlite3
from utils.config import config
from utils.logger import Logger

class Memory:
    """
    Local persistent memory using SQLite to correlate findings across scans.
    """
    def __init__(self):
        self.db_path = config.db_path
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT,
                    type TEXT,
                    data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            Logger.error(f"Failed to initialize database: {e}")

    def store(self, target, f_type, data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO findings (target, type, data) VALUES (?, ?, ?)',
                           (target, f_type, str(data)))
            conn.commit()
            conn.close()
        except Exception as e:
            Logger.error(f"Failed to store finding: {e}")

    def query(self, target):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT type, data, timestamp FROM findings WHERE target = ?', (target,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            Logger.error(f"Failed to query database: {e}")
            return []

memory = Memory()
