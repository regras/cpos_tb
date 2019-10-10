import sqlite3
import logging
import block
import blockchain
import leaf
import leafchain
import parameter
from collections import deque, Mapping, defaultdict
import pickle
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
    cursor.execute("""CREATE TABLE IF NOT EXISTS localChains (
        id integer NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        leaf_head text,
        leaf_prev_head text,
        leaf_prev_hash text,
        leaf_prev_round integer,
        leaf_prev_arrive_time text,
        leaf_prev2_hash text,
        leaf_prev2_round integer,
        leaf_prev2_arrive_time text,
        fork integer,
        PRIMARY KEY (id,leaf_head))""")
    db.commit()
    db.close()

def setForkFromBlock(block_hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    query = cursor.fetchone()

    if(query):
        forks = query[0]
        forks = int(forks) + 1
        cursor.execute("UPDATE localChains SET fork = '%s' WHERE hash = '%s'" % (forks, block_hash))

    db.commit()
    db.close()

def clearForkFromBlock(block_hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    query = cursor.fetchone()
    forks = query[0]
    if(int(forks) > 0):
        forks = int(forks) - 1
        cursor.execute("UPDATE localChains SET fork = '%s' WHERE hash = '%s'" % (forks, block_hash))
    db.commit()
    db.close()

def checkForkFromBlock(block_hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    forks = cursor.fetchone()
    db.commit()
    db.close()
    return int(forks)

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
def checkChainIsLeaf(leaf_db):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    index = leaf_db[0] + 1
    cursor.execute("select * from localChains where id = %d" % index)
    queries = cursor.fetchall()
    if queries:
        for query in queries:
            #print("dados bloco apos fork")
            #print(query[0])
            #print(query[2])
            prev_hash = query[2]
            if (prev_hash == leaf_db[3]):
                return True
        return False
    else:
        return False    

def dbCheckLeaf(bc):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select * from localChains T1 where T1.id = (select max(T2.id) from localChains T2 where T1.leaf_head = T2.leaf_head group by T2.leaf_head)')
    leafs_db = cursor.fetchall()
    i = 1
    l = None
    if leafs_db:
        for leaf_db in leafs_db:
            #print(leaf_db)
            #check if the Chain is Valid
            #checkChainIsLeaf(leaf_db)
            if i == 1:
                if(not checkChainIsLeaf(leaf_db)):
                    l = leafchain.Leafchain(leaf_db)
                    i = 0 
            else:
                if(not checkChainIsLeaf(leaf_db)):
                    l.appendLeaf(leaf_db)
    else:
        #leaf_db = cursor.fetchone()
        l = leafchain.Leafchain()
        writeChainLeaf(l.leaf[0][0],bc.getLastBlock())

    leafs = l.getLeafs()
    for k,t in leafs.iteritems():
        print(t[0].leaf_hash)
        print(t[0].leaf_round)
        print(t[0].leaf_arrivedTime)
        
    db.commit()
    db.close()
    return l
    
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

def writeChainLeaf(l, b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()

    try:
        if isinstance(b, list) and isintance(l, list):
            cursor.executemany('INSERT INTO localChains VALUES (?,?,?,?,?,?,?,?)', b)
            print("problem on insertion funcion----")
        else: 
            #print("HEAD NOVO BLOCO")
            #print(l.leaf_head)     
            cursor.execute('INSERT INTO localChains VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time'],
                    l.__dict__['leaf_head'],
                    l.__dict__['leaf_prev_head'],
                    l.__dict__['leaf_prev_hash'],
                    l.__dict__['leaf_prev_round'],
                    l.__dict__['leaf_prev_arrivedTime'],
                    l.__dict__['leaf_prev2_hash'],
                    l.__dict__['leaf_prev2_round'],
                    l.__dict__['leaf_prev2_arrivedTime'],
                    '0'
                    ))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block in the same chain')
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

def blockHashQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM localChains WHERE hash = ?', (messages[1],))
    b = cursor.fetchone()
    db.close()
    return b

def removeBlock(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("DELETE FROM localChains WHERE hash = '%s'" % messages[1])
    db.commit()
    db.close()

def removeLeafChain(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT max(id), hash, fork from localChains where leaf_head = '%s' and fork <> 0" % messages[1])
    query = cursor.fetchone()
    print("QUERY")
    print(query)

    if(query[1]):
        block_hash = query[1]
        fork = query[2]
        print("Fork")
        print(fork)
        fork = int(fork) - 1
        cursor.execute("DELETE FROM localChains where leaf_head = '%s' and id > (SELECT max(id) from localChains where leaf_head = '%s' and fork <> 0)" % (messages[1],messages[1]))
        cursor.execute("UPDATE localChains set fork = %d where hash = '%s' " % (fork, block_hash))
        db.commit()
    else:
        print("REMOVE ALL CHAIN")
        print("HEAD")
        print(messages[1])
        #remove all chain.
        cursor.execute("SELECT *  from localChains where id = (SELECT min(id) from localChains where leaf_head = '%s')" % messages[1])
        query = cursor.fetchone()
        if(query[0]):
            cursor.execute("DELETE FROM LocalChains where leaf_head = '%s'" % messages[1])
            db.commit()
            #if(fork == 0):
            #    if(not checkChainIsLeaf(query)):
            #        block_hash = query[3]
            #        cursor.execute("DELETE FROM LocalChains where hash = '%s'" % block_hash)
            #        prev_hash = query[2]
            #        cursor.execute("SELECT fork from localChains where hash = '%s'" % prev_hash)
            #        if (query[0]):
            #            fork = query[0]
            #            if (fork > 0):
            #                fork = int(fork) - 1
            #                cursor.execute("UPDATE localChains set fork = %d where hash = '%s' " % (fork, prev_hash))
            prev_hash = query[2]
            cursor.execute("SELECT * from localChains where hash = '%s'" % prev_hash)
            query = cursor.fetchone()
            fork = query[16]
            #print("prev hash")
            #print(prev_hash)
            #print("fork")
            #print(fork)
            #print("Hash block do fork")
            #print(prev_hash)
            if(int(fork) == 0):
                if(not checkChainIsLeaf(query)):
                    print("not checkChainIsLeaf")
                    cursor.execute("DELETE FROM LocalChains where hash = '%s'" % prev_hash)
                    db.commit()

                    #remove one unit of the fork point before the fork that was removed
                    prev_hash = query[2]
                    cursor.execute("SELECT fork from localChains where hash = '%s'" % prev_hash)
                    query = cursor.fetchone()
                    if(query[0]):
                        fork = query[0]
                        if(int(fork) > 0):
                            fork = int(fork) - 1
                            cursor.execute("UPDATE localChains set fork = %d where hash = '%s' " % (fork, prev_hash))
                            db.commit()
                            
            elif(int(fork) > 0):
                print("Update fork point")
                fork = int(fork) - 1
                cursor.execute("UPDATE localChains set fork = %d where hash = '%s' " % (fork, prev_hash))       
                db.commit()

              


    db.commit()
    db.close()
    #clearForkFromBlock(block_hash) 
    
def blocksQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id BETWEEN ? AND ?', (messages[1],messages[2]))
    l = cursor.fetchall()
    db.close()
    return l

def leavesQuery():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select * from localChains T1 where T1.id = (select max(T2.id) from localChains T2 where T1.leaf_head = T2.leaf_head group by T2.leaf_head)')
    leafs_db = cursor.fetchall()
    db.close()
    return leafs_db

def searchForkPoint(leaf):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" % leaf[2])
    leafs_db = cursor.fetchone()
    db.close()
    return leafs_db

def dbGetAllChain(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE leaf_head = '%s' ORDER BY id ASC" % messages[0])
    leafs_db = cursor.fetchall()
    db.close()
    return leafs_db
    

def dbCheckUnknowChain(messages):
    heads = defaultdict(list)
    hashes = pickle.loads(messages[0])
    
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
   
    for k,l in list(hashes.iteritems()):
        cursor.execute("select leaf_head from localChains WHERE hash = '%s'" % l[0])
        query = cursor.fetchone()
        heads[k].append(query[0])

    #verifyng chains that is no leaf more
    cursor.execute('select * from localChains T1 where T1.id = (select max(T2.id) from localChains T2 where T1.leaf_head = T2.leaf_head group by T2.leaf_head)')
    leafs_db = cursor.fetchall()
    if(leafs_db):
        for leaf_db in leafs_db:
            if(checkChainIsLeaf(leaf_db)):
                heads[max(heads) + 1].append(leaf_db[8])

    
    #return all chains that is leaf on the local blockchain
    
    cursor.execute("SELECT distinct leaf_head FROM localChains")
    leafs_db = cursor.fetchall()
    validHeads = []
    if(leafs_db):
        for leaf_db in leafs_db:
            include = False
            for k,l in list(heads.iteritems()):
                if(leaf_db[0] == l[0]):
                    include = True
                    break

            if(not include):
                validHeads.append(leaf_db[0])
    print("validHeads")
    print(validHeads)
    #for k, l in list(heads.iteritems()):
        
    #    print(l[0])
    #    if (k < max(heads)):
    #        query = query + "leaf_head <> '%s' or "
    #    else:
    #        query = query + "leaf_head <> '%s' "
   
    #param = ""
    #for k, l in list(heads.iteritems()):
    #    if(k < max(heads)):
    #        param = param + str(l[0]) + ", "
    #    else:
    #        param = param + str(l[0])
    
    #print("PARAMETROS")
    #print(param)
    #cursor.execute(query % (param))
    #query = cursor.fetchall()
    db.close()
    return pickle.dumps(validHeads)

    
def dbCheckChain(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()

    cursor.execute("SELECT id,leaf_head FROM localChains WHERE hash ='%s'" % messages[0])
    query = cursor.fetchone()
    prefixId = query[0]
    prefixHead = query[1]

    cursor.execute("SELECT id,leaf_head FROM localChains WHERE hash ='%s'" % messages[1])
    query = cursor.fetchone()
    sufixId = query[0]
    sufixHead = query[1]

    query = None
    if(prefixHead == sufixHead):
        print("Same Chain")
        cursor.execute("SELECT * FROM localChains WHERE id > %d and leaf_head = '%s' order by id asc " % (prefixId, prefixHead))
        query = cursor.fetchall()
        db.close()
        return query
    #else:
    #    cursor.execute("SELECT id,leaf_prev_head, leaf_head FROM localChains WHERE hash ='%s'" % messages[1])
    #    query = cursor.fetchone()
    #    sufixId = query[0]
    #    sufixPrevHead = query[1]
    #    sufixHead = query[2]

    #    if(sufixPrevHead == prefixHead):
            #encontra o ponto de fork entre as cadeias
    #       cursor.execute("SELECT * FROM localChains WHERE id = ()" % (prefixId, prefixHead, sufixHead))
            #the chain is sufix of the other chain
    #       cursor.execute("SELECT * FROM localChains WHERE id > %d and (leaf_head = '%s' or leaf_head = '%s')" % (prefixId, prefixHead, sufixHead))
    #       query = cursor.fetchall()
    #       db.close()
    #       return query

        #else:
        #    heads = defaultdict(list)
        #    cursor.execute("SELECT id,leaf_prev_head, leaf_head FROM localChains WHERE hash ='%s'" % messages[1])
        #    query = cursor.fetchone()
        #    sufixPrevHead = query[1]
        #    sufixHead = query[2]
        #    l = 0
        #    heads[l].append(sufixHead)
        #    l = 1
        #    while(sufixPrevHead != prefixHead):
        #        if(sufixPrevHead != parameter.FIRST_HEAD):
        #            heads[l].append(sufixPrevHead)
        #            l = l + 1
        #            cursor.execute("SELECT min(id),leaf_prev_head, leaf_head FROM localChains WHERE leaf_hash ='%s'" % sufixPrevHead)
        #            query = cursor.fetchone()
        #            sufixPrevHead = query[1]
        #        else:
        #            return None
        #    heads[l].append(prefixHead)
        #    print("HEADS")
        #    query = "SELECT * FROM localChains WHERE id > %d and (leaf_head = "
        #    for k,l in list(heads.iteritems()):
        #        if (k != max(heads)):
        #            query = query + str(l[0]) + " or leaf_head = "
        #        else:
        #            query = query + str(l[0]) + " )"
        #    cursor.execute(query)
        #    query = cursor.fetchall()
        #    return query    

    
        
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
