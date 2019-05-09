import sqlite3
import logging
import block
import blockchain

logger = logging.getLogger(__name__)
databaseLocation = 'blocks/blockchain.db'

# write methods work with block objects instead of tuple from sqlite db

def dbConnect():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
        id integer NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id, hash))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS chain (
        id integer NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id))""")
    db.commit()
    db.close()

def dbCheck():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id = (SELECT MAX(id) FROM chain)')
    # Last block from own database
    lastBlock_db = cursor.fetchone()
    bc = blockchain.Blockchain(lastBlock_db)
    # Empty database
    if not lastBlock_db:
        genesis = bc.getLastBlock()
        print(genesis.blockInfo())
        writeChain(genesis)
        #wwriteBlock(genesis)

    db.commit()
    db.close()
    return bc

def writeBlock(b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()

    try:
        if isinstance(b, list):
            cursor.executemany('INSERT INTO blocks VALUES (?,?,?,?,?,?,?,?)', b)
        else:
            cursor.execute('INSERT INTO blocks VALUES (?,?,?,?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()

def writeChain(b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        if isinstance(b, list):
            cursor.executemany('INSERT INTO chain VALUES (?,?,?,?,?,?,?,?)', b)
        else:
            cursor.execute('INSERT INTO chain VALUES (?,?,?,?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()

def replaceChain(b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    print('BLOCK TO INSERT OR REPLACE ON CHAIN TABLE', b)
    try:
        if isinstance(b, tuple):
            cursor.execute('REPLACE INTO chain VALUES (?,?,?,?,?,?,?,?)', b)
        else:
            cursor.execute('INSERT OR REPLACE INTO chain VALUES (?,?,?,?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()

def forkUpdate(index):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id = {0} AND prev_hash = (SELECT hash FROM chain WHERE id = {1})'.format(index,index-1))
    b = cursor.fetchone()
    #cursor.execute('REPLACE INTO chain VALUES (?,?,?,?,?,?,?)', b)
    db.close()
    return b


def blockQueryFork(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
    b = cursor.fetchall()
    db.close()
    return b

def blockQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id = ?', (messages[1],))
    b = cursor.fetchone()
    db.close()
    return b

def blocksQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id BETWEEN ? AND ?', (messages[1],messages[2]))
    l = cursor.fetchall()
    db.close()
    return l

def blocksListQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    idlist = messages[1:]
    #idlist = [int(i) for i in messages[1:]]
    cursor.execute('SELECT * FROM chain WHERE id IN ({0})'.format(', '.join('?' for _ in idlist)), idlist)
    l = cursor.fetchall()
    db.close()
    return l

def dbtoBlock(b):
    """ Transform database tuple to Block object """
    if isinstance(b, block.Block) or b is None:
        return b
    else:
        return block.Block(b[0],b[2],b[1],b[4],b[7],b[3],b[6])

def getLastBlockIndex():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT MAX(id) FROM chain')
    l = cursor.fetchone()
    l = int(l[0])
    db.close()
    return l

def quantityofBlocks():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM blocks')
    l = cursor.fetchone()
    if l is not None:
        l = int(l[0])
    else:
        l = 0
    db.close()
    return l

def getQuantityForks():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM (SELECT COUNT(*) FROM blocks GROUP BY id HAVING COUNT(*) > 1)')
    l = cursor.fetchone()
    if l is not None:
        l = int(l[0])
    else:
        l = 0
    db.close()
    return l

def getallchain():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain')
    l = cursor.fetchall()
    chain = []
    for b in l:
        chain.append(dbtoBlock(b))

    db.close()
    return chain

def getallblocks():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks')
    l = cursor.fetchall()
    tree=[]
    for b in l:
        tree.append(dbtoBlock(b))

    db.close()
    return tree
