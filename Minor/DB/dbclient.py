import sqlite3 as sl
from datetime import datetime

def initConnect():
    con = sl.connect('Minor\locker.db')
    #print(con)
    return con

#### DDL for Create ####
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
def createTableRequest():
    con = initConnect();
    with con:
        con.execute("""
           CREATE TABLE REQUEST (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            requestDate TEXT,
            orderNo TEXT,
            sdmOrder TEXT,
            requestData TEXT,
            responseData TEXT,
            status INTEGER
           );
        """)

##### KEY MANAGEMENT ######
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

##### LOCKER MANAGEMENT ######
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
        con.commit()

def clearLockerOfYesterday():
    con = initConnect();

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d")
    sql = 'delete from LOCKER where reserveDate < \''+ current_time+'\''
    #print(sql)
    data = [(current_time)]
    with con:
        con.execute(sql)
        con.commit()

##### REQUEST MANAGEMENT ######
def createRequest(input):
    con = initConnect();
    cur = con.cursor()
    sql = 'INSERT INTO REQUEST ( requestDate, orderNo, sdmOrder, requestData) values(?, ?, ? ,? ,?)'
    data = [input]
    with con:
        con.executemany(sql, data)
        con.commit()
        return cur.lastrowid

def updateResponse(input,rowid):
    con = initConnect();
    sql = 'UPDATE REQUEST set responseData = \''+ input[0] +'\' , status = \''+ input[1] +'\' where id = \''+ rowid +'\' '
    with con:
        con.execute(sql)

# def updateResponse(input,sdm):
#     con = initConnect();
#     sql = 'UPDATE REQUEST set responseData = \''+ input[0] +'\' , status = \''+ input[1] +'\' where orderNo = \''+ input[2] +'\' and sdmOrder = \''+ sdm +'\' '
#     if sdm == '':
#          sql = 'UPDATE REQUEST set responseData = \''+ input[0] +'\' , status = \''+ input[1] +'\' where orderNo = \''+ input[2] +'\' '
#     with con:
#         con.execute(sql)