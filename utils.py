from database import get_conn
def query_all(query,params=()):
    conn=get_conn()
    cur=conn.cursor()
    cur.execute(query,params)
    rows=cur.fetchall()
    conn.close()
    return rows
def query_one(query,params=()):
    conn=get_conn()
    cur=conn.cursor()
    cur.execute(query,params)
    row=cur.fetchone()
    conn.close()
    return row
def execute(query,params=()):
    conn=get_conn()
    cur=conn.cursor()
    cur.execute(query,params)
    conn.commit()
    lastid=cur.lastrowid
    conn.close()
    return lastid