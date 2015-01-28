import sqlite3 as lite

con = lite.connect("dbFile.db")
cur = con.cursor()

cur.execute("SELECT * FROM inverted_index")
data = cur.fetchall()
print data

cur.execute("SELECT * FROM pagerank")
data = cur.fetchall()
print data

con.commit()
con.close()