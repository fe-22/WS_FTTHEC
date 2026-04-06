import sqlite3
from pathlib import Path

path = Path('db.sqlite3')
print('db exists', path.exists(), path.resolve())
conn = sqlite3.connect(str(path))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for row in cur.fetchall():
    print(row[0])
conn.close()
