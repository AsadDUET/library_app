import sqlite3
con = sqlite3.connect('library_data.db')

cur = con.cursor()

cur.execute('''DROP TABLE users''')
cur.execute('''DROP TABLE exchange''')

cur.execute('''CREATE TABLE IF NOT EXISTS users
               (name text, id text, stdid text PRIMARY KEY)''')

cur.execute('''CREATE TABLE IF NOT EXISTS books
               (name text, id text PRIMARY KEY, pcs INTEGER )''')

cur.execute('''CREATE TABLE IF NOT EXISTS exchange
               (book_id text, std_id text , status INTEGER,CONSTRAINT unq UNIQUE (book_id, std_id, status) )''')
               
# Insert Student
try:
    cur.execute("INSERT INTO users VALUES ('Rana','2','123456')")
except Exception as e:
    print(e," User id already exists. ",)

## Insert Book
try:
    cur.execute("INSERT INTO books VALUES ('English','3',25)")
except Exception as e:
    print(e," Book id already exists. ",)

## Insert exchange
try:
    cur.execute("INSERT INTO exchange VALUES ('0','123456',1)")
except Exception as e:
    print(e, "Multiple copy not allowed")

##UPDATE exchange
try:
    cur.execute('UPDATE exchange SET status=0 WHERE book_id=1 AND std_id=123456')
except Exception as e:
    print(e)
    cur.execute('DELETE FROM  exchange  WHERE book_id=1 AND std_id=123456 AND status=1')




# Save (commit) the changes
con.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.

try:
    for row in cur.execute('SELECT * FROM books'):
        print (row)

except Exception as e:
    print(e)
print("*************")
try:
    for row in cur.execute('SELECT * FROM exchange'):
        print (row)

except Exception as e:
    print(e)
print("*************")

# ## All Book list
try:
    book_ids=[]
    borrowed=[]
    row_datas=[]
    for row in cur.execute('SELECT * FROM books ' ):
        book_ids.append(row[1])
    print(book_ids)
    for id in book_ids:
        borrowed.append(cur.execute(f'SELECT COUNT(*) FROM exchange WHERE book_id={id} AND status=1').fetchall()[0][0])
    print(borrowed)
    print("Name","ID", "Borrowed","Available","Total")
    for n, row in enumerate(cur.execute('SELECT * FROM books ')):
        row_datas.append((n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2]))
        print(n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2])
    print(row_datas)
except Exception as e:
    print(e, "Table or data Not Found")


## All Student List
try:
    for row in cur.execute('SELECT * FROM users ' ):
        print(row)
except Exception as e:
    print(e, "Table or data Not Found")
# print(cur.execute('SELECT COUNT(*) FROM exchange WHERE status=1').fetchall()[0][0])

con.close()