import sqlite3

conn = sqlite3.connect('rssdownload.db')
c = conn.cursor()
c.execute('''CREATE TABLE posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              dateadded date,
              datepublished text,
              feed text,
              category text,
              link text,
              title text,
              description text,
              exported bool default False)''')
conn.commit()
conn.close()
