import sqlite3
import os
import datetime
import csv

class HistoryManager:
    def __init__(self, db_path="history.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', db_path)
        self._init_db()

    def _init_db(self):
        """Initialize the database table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posted_videos
                     (url TEXT PRIMARY KEY, 
                      title TEXT, 
                      date TEXT, 
                      account TEXT, 
                      status TEXT,
                      file_path TEXT)''')
        conn.commit()
        conn.close()

    def add_entry(self, url, title, account, status="Posted", file_path=""):
        """Add or update a video entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''INSERT OR REPLACE INTO posted_videos 
                         (url, title, date, account, status, file_path) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (url, title, date_str, account, status, file_path))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    def check_exists(self, url):
        """Check if a URL has already been posted."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT status FROM posted_videos WHERE url=?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def get_all_history(self):
        """Retrieve all history for export."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM posted_videos ORDER BY date DESC")
        rows = c.fetchall()
        conn.close()
        return rows

    def export_to_txt(self, output_path="history_export.txt"):
        """Export history to a readable TXT file."""
        rows = self.get_all_history()
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"{'Date':<22} | {'Account':<15} | {'Status':<10} | {'Title':<40} | {'URL'}\n")
                f.write("-" * 120 + "\n")
                for r in rows:
                    # r: url, title, date, account, status, file_path
                    f.write(f"{r[2]:<22} | {r[3]:<15} | {r[4]:<10} | {r[1][:38]:<40} | {r[0]}\n")
            return True
        except Exception as e:
            print(f"Export Error: {e}")
            return False
