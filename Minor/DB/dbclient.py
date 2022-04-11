import sqlite3 as sl
from datetime import datetime

def initConnect():
    con = sl.connect('Minor\locker.db')
    #print(con)
    return con

def createTable():
    con = initConnect();
    with con:
        con.execute("""
            CREATE TABLE LOCKER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                reserveDate TEXT,
                orderNo TEXT,
                sdmOrder TEXT,
                lockerNo TEXT,
                status TEXT,
                status2 INTEGER
            );
        """)

def createTableKey():
    con = initConnect();
    with con:
        con.execute("""
            CREATE TABLE KEY (
                encrypted TEXT
            );
        """)
def createKey(input):
    con = initConnect();
    sql = 'INSERT INTO KEY ( encrypted) values( \''+input+'\')'
    data = []
    with con:
        con.execute(sql)
def clearKey():
    con = initConnect();
    sql = 'DELETE FROM KEY'
    with con:
        con.execute(sql)

def getKey():
    con = initConnect();
    sql = 'select encrypted FROM KEY LIMIT 1'
    with con:
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

def createLocker(input):
    con = initConnect();
    sql = 'INSERT INTO LOCKER ( reserveDate, orderNo, sdmOrder, lockerNo, status) values(?, ?, ? ,? ,?)'
    data = [input]
    # data = [
    #     (1, 'Alice', 21),
    #     (2, 'Bob', 22),
    #     (3, 'Chris', 23)
    # ]
    with con:
        con.executemany(sql, data)

def clearLockerOfYesterday():
    con = initConnect();

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d")
    sql = 'delete from LOCKER where reserveDate < \''+ current_time+'\''
    #print(sql)
    data = [(current_time)]
    with con:
        con.execute(sql)