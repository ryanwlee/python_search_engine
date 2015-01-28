import sqlite3 as lite

con = lite.connect("dbFile.db")
cur = con.cursor()
cur.execute('CREATE TABLE pagerank(doc_id INTEGER, value FLOAT);')

for i in range(0,98):
 query = 'INSERT INTO pagerank VALUES('+str(i)+', '+str(float(i))+');'
 cur.execute(query)

cur.execute('CREATE TABLE inverted_index(word TEXT, doc TEXT, doc_id INTEGER);')

item = 'apple'
doc = 'https://www.google.ca/#q='

for i in range(0,98):
 query = 'INSERT INTO inverted_index VALUES(\''+str(item)+'\', \''+str(doc)+str(i)+'\', \''+str(i)+'\');'
 cur.execute(query)

con.commit()
con.close()
