import sqlite3

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()
cur.execute(
    """
ALTER TABLE post_post RENAME TO posts_post;
"""
)
