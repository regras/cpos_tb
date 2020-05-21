#!/usr/bin/env python
import sqlite3
import logging
from block import Block
import block
from block import Block
import blockchain
import leaf
import parameter
import datetime
import time
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
        idChain integer NOT NULL,
        id integer NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        fork integer,
        stable integer,
        subuser integer,
        deny integer,
        PRIMARY KEY (id,idChain))""")

    #cursor.execute("""CREATE TABLE IF NOT EXISTS log_mine (
    #  id text NOT NULL,
    #  time text,
    #  chain text,
    #  primary key (id))""")
    
    #cursor.execute("""CREATE TABLE IF NOT EXISTS log_listen (
    #  id text NOT NULL,
    #  time text,
    #  chain text,
    #  accepted text, 
    #  node text,
    #  primary key (id))""")
 
    cursor.execute("""CREATE TABLE IF NOT EXISTS log_fork (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      startBlock integer default 0,
      endBlock integer default 0,
      startFork text default 0,
      endFork text default 0)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS log_block (
        idAutoNum INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        round integer,
        arrive_time text,
        node text,
        prev_hash text,
        hash,
        status integer,
        UNIQUE (idAutoNum,hash))""")
     
    db.commit()
    db.close()
def getLastStableBlock(lastBlockSimulation):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT max(id) FROM localChains WHERE id > '%d'" % lastBlockSimulation)
    query = cursor.fetchone()
    db.close()
    if(query):
        return query[0]
    else:
        return None

####functions to sync
def getHead(blockHash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT leaf_head from localChains WHERE hash = '%s'" % blockHash)
    query = cursor.fetchone()
    if(query):
        db.close()
        return query[0]
    else:
        db.close()
        return None

def verifyBlockIsLeaf(blockHash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT hash from localChains WHERE prev_hash = '%s' limit 1" % blockHash)
    query = cursor.fetchone()
    if(query):
        db.close()
        return False
    else:
        db.close()
        return True
    
def verifyRoundBlock(blockId,blockRound):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT round from localChains WHERE id = %d limit 1" % blockId)
    query = cursor.fetchone()
    db.close()
    if(query):
        if(blockRound <= query[0]):
            return True, query[0]
        else:
            return False, query[0]
    else:
        return True, None

def dbReqBlocks(messages):
    if(messages):
        print("dbReqBlocks")
        forkHash = messages[0]
        headChains = pickle.loads(messages[1])
        blockHash = messages[2]
        for k,l in list(headChains.iteritems()):
            if(dbIsSameChain(blockHash, l[0])):
                subChain = dbGetSubChain(blockHash, l[0])
                return pickle.dumps(subChain)
        subChain = dbGetSubChain(blockHash, forkHash)
    return pickle.dumps(subChain)

def dbGetSubChain(blockHash, forkHash):
    subChain = defaultdict(list)
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    print("BlockHash")
    print(blockHash)
    print("pointHash")
    print(forkHash)
    cursor.execute("SELECT id from localChains WHERE hash = '%s'" % blockHash)
    query = cursor.fetchone()
    if(query):
        idBlockHash = query[0]

    cursor.execute("SELECT id from localChains WHERE hash = '%s'" % forkHash)
    query = cursor.fetchone()
    if(query):
        idForkHash = query[0]
    difIndex = int(idBlockHash - idForkHash)
    i = 0

    cursor.execute("SELECT prev_hash FROM  localChains WHERE hash = '%s'" % blockHash)
    query = cursor.fetchone()
    blockHash = query[0]

    while(difIndex > 1):
        cursor.execute("SELECT * FROM  localChains WHERE hash = '%s'" % blockHash)
        query = cursor.fetchone()
        if(query):
            subChain[i].append(query)
            i = i + 1
        blockHash = query[2]
        difIndex = difIndex - 1
    return subChain


def dbIsSameChain(blockHash, pointHash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT id from localChains WHERE hash = '%s'" % blockHash)
    query = cursor.fetchone()
    if(query):
        idBlockHash = query[0]

    cursor.execute("SELECT id from localChains WHERE hash = '%s'" % pointHash)
    query = cursor.fetchone()
    if(query):
        idPointHash = query[0]
    difIndex = int(idBlockHash - idPointHash)

    while(difIndex > 0):
        cursor.execute("SELECT prev_hash FROM localChains WHERE hash = '%s'" % blockHash)
        query = cursor.fetchone()
        if(query):
            if(query[0] == pointHash):
                db.close()
                return True
            else:
                blockHash = query[0]
                difIndex = difIndex - 1
        else:
            db.close()
            return False
    db.close()
    return False

def dbKnowBlock(blockHash):
    try:
        db = sqlite3.connect(databaseLocation)
        cursor = db.cursor()
        cursor.execute("SELECT * from localChains WHERE hash = '%s'" % blockHash)
        query = cursor.fetchone()
        if(query):
            db.close()
            return True
        else:
            db.close()
            return False
    except Exception as e:
        print(str(e))
        return False

def dbReqBlock(messages):
    try:
        blockHash = messages[0]
        db = sqlite3.connect(databaseLocation)
        cursor = db.cursor()
        cursor.execute("SELECT * from localChains WHERE hash = '%s'" % blockHash)
        query = cursor.fetchone()
        if(query):
            db.close()
            return pickle.dumps(query)
        else:
            db.close()
            return None
    except Exception as e:
        print(str(e))
        return None

#####end functions to sync

def bournChain(head):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT min(id) FROM localChains WHERE leaf_head = '%s'" % head)
    query = cursor.fetchone()
    db.close()
    if(query):
        return query[0]
    else:
        return None

def getPrev3Block(hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT round, prev_hash, arrive_time FROM localChains WHERE hash = '%s'" % hash)
    query = cursor.fetchone()
    db.close()
    if(query):
        return query
    else:
        return None

    
def checkActiveFork(numBlocks):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM log_fork WHERE startBlock > %d and status = 1" % (numBlocks)) 
    queries = cursor.fetchall()
    db.close()
    if(queries):
        return True
    else:
        return False
def getRoundByIndex(index):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT round from localChains where id = %d" %index)
    query = cursor.fetchone()
    if(query):
        return query[0]
    else:
        return None
def getBlock(hash=None):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    if(hash):
        cursor.execute("SELECT * from localChains where hash = '%s'" % hash)
    else:
        cursor.execute("SELECT * from localChains where id = (select max(id) from localChains)")
    query = cursor.fetchone()
    if(query):
        return dbtoBlock(query)
    else:
        return None

def getBlocks(numBlocks):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * from log_block WHERE idAutoNum > %d" % (numBlocks))
    queries = cursor.fetchall()
    db.close()
    return queries

def dbNumBlocks(numBlocks):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) from log_block WHERE idAutoNum > %d" % (numBlocks))
    query = cursor.fetchone()
    db.close()
    if(query):
        return query[0]
    else:
        return None

def getForks(lastForks):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * from log_fork")
    queries = cursor.fetchall()
    sendQueries = {}
    for query in queries:
        sentFork = False
        for lastFork in lastForks:
            fork = lastForks[lastFork][0]
            if(fork[0] == query[0]):
                print("Retorna fork")
                print(fork[0])
                sentFork = True
                break
        if(not sentFork):
            if(sendQueries):
                index = max(sendQueries) + 1
            else:
                index = 0
            sendQueries[index] = []
            sendQueries[index].append(query)

    db.close()
    print("sendQueries")
    print(sendQueries)
    return sendQueries

def dbNumForks():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) from log_fork")
    query = cursor.fetchone()
    db.close()
    if(query):
        return query[0]
    else:
        return None

def hasDb(hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT hash from localChains WHERE hash = '%s'" % hash)
    query = cursor.fetchone()
    db.close()
    if query:
        return True
    else:
        return False

def setStableBlocks(round):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    round = round - parameter.roundTolerancy
    cursor.execute("SELECT id, hash from localChains t1 WHERE stable = 0 and deny = 0 and EXISTS (SELECT hash FROM localChains t2 WHERE t1.id = t2.id and t2.deny = t1.deny GROUP BY id HAVING COUNT(*) = 1)")
    queries = cursor.fetchall()
    if queries:
        for query in queries:
            cursor.execute("UPDATE localChains set stable = 1 WHERE round < %d AND stable = 0 AND hash = '%s'" % (round, query[1]))
            db.commit()
    cursor.execute("SELECT COUNT(*) FROM localChains WHERE stable = 1")
    queries = cursor.fetchone()
    if queries:
        stableBlocks = queries[0]

    db.commit()
    db.close()
    return stableBlocks

#def setLogFork(head, localtime, status, startIndex = 0, endIndex = 0, leaf_hash = None, hash1 = None, hash2 = None):
def setLogFork(startBlock, endBlock, startFork, endFork):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    #if(status == 1):
    print("ENTROU SETLOGFORK")
    cursor.execute('INSERT INTO log_fork (startBlock, endBlock, startFork, endFork) VALUES (?,?,?,?)',(
    startBlock,
    endBlock,
    startFork,
    endFork))
    db.commit()
    db.close()
    return True
    #else:
    #    print("LOG REMOVE FORK")
    #    print(leaf_hash)
    #    cursor.execute('SELECT id, hash1, hash2 from log_fork WHERE status = "1"')
    #    queries = cursor.fetchall()
    #    j = 0
    #    lenMin = 0
    #    foundFork = False
    #    for query in queries:
    #        hash1 = query[1]
    #        hash2 = query[2]
    #        id = query[0]
    #        i = 0
    #        hash = hash1
    #        len = 0
    #        while(i <= 1):
    #            while(hash):
    #                print("HASH")
    #                print(hash)
    #                if(hash == leaf_hash):
    #                    if(len <= lenMin or j == 0):
    #                       idMin = id
    #                       lenMin = len
    #                       j = 1
    #                    len = 0
    #                    hash = None
    #                    foundFork = True
    #                else:
    #                    cursor.execute("SELECT hash from localChains where prev_hash = '%s'" % hash)
    #                    queryChains = cursor.fetchone()
    #                    if(queryChains):
    #                        len = len + 1
    #                        hash = queryChains[0]
    #                    else:
    #                        len = 0
    #                        hash = None
    #            i = i + 1
    #            if(i == 1):
    #               hash = hash2

    #    if(foundFork):
    #         endTime = int(time.mktime(datetime.datetime.now().timetuple()))
    #         cursor.execute('UPDATE log_fork set endBlock = %d, endTime = %d, status = "0" WHERE id = %d' %(endIndex, endTime, idMin))
    #         db.commit()
    #         db.close()
    #         return True

    #    db.close()
    #    return False
     
def setLogBlock(b, accepted):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    if(b):
        try:
            cursor.execute('INSERT INTO log_block (id, round, arrive_time, node, prev_hash, hash, status) VALUES (?,?,?,?,?,?,?)',(
                b.__dict__['index'],
                b.__dict__['round'],
                b.__dict__['arrive_time'],
                b.__dict__['node'],
                b.__dict__['prev_hash'],
                b.__dict__['hash'],
                accepted))
            
        except sqlite3.IntegrityError:
            logger.warning('db insert duplicated block on log_block')
        finally:
            db.commit()
            db.close() 

#def setLogMine(l, b):
#    db = sqlite3.connect(databaseLocation)
#    cursor = db.cursor()

#    try:
       #print("HEAD NOVO BLOCO")
       #print(l.leaf_head)     
#        cursor.execute('INSERT INTO log_mine VALUES (?,?,?)',(
#        b.__dict__['hash'],
#        b.__dict__['arrive_time'],
#        l.__dict__['leaf_head']))

#    except sqlite3.IntegrityError:
#        logger.warning('db insert duplicated block in the same chain')
    #finally:
#    db.commit()
#    db.close()    

#def setLogMine(l, b):
#    db = sqlite3.connect(databaseLocation)
#    cursor = db.cursor()
#    cursor.execute('INSERT INTO log_mine VALUES (?,?,?)', (
#                    b.__dict__['hash'],
#                    b.__dict__['arrive_time'],
#                    l.__dict__['leaf_head']))
#    db.commit()
#    db.close()


def setForkFromBlock(block_hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    query = cursor.fetchone()

    if(query):
        forks = query[0]
        forks = int(forks) + 1
        cursor.execute("UPDATE localChains SET fork = %d WHERE hash = '%s'" % (forks, block_hash))

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

def dbInsertFirstBlock():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select * from localChains')
    leafs_db = cursor.fetchall()
    if not leafs_db:
        b = block.Block(index=0,prev_hash="",round=0,node="",b_hash="",arrive_time=parameter.GEN_ARRIVE_TIME)
        createNewChain(b)
    db.commit()
    db.close()
    return True
    
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

def writeChainLeaf(idChain,b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO localChains VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                idChain,
                b.__dict__['index'],
                b.__dict__['round'],
                b.__dict__['prev_hash'],
                b.__dict__['hash'],
                b.__dict__['node'],
                b.__dict__['mroot'],
                b.__dict__['tx'],
                b.__dict__['arrive_time'],
                '0',
                '0',
                b.__dict__['subuser'],
                '0'
                ))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block in the same chain')
    finally:
        db.commit()
        db.close()
def getIdChain(blockHash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        cursor.execute("select idChain from localChains where hash = '%s'" %blockHash)
        query = cursor.fetchone()
        db.close()
        if(query):
            return query[0]
        else:
            return None
    except sqlite3.IntegrityError:
        print("impossible to return chain id")

def blockIsPriority(blockIndex,blockHash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        cursor.execute('select hash from localChains where id = %d' %blockIndex)
        queries = cursor.fetchall()
        db.close()
        if(queries):
            for query in queries:
                if(int(query[0],16) < int(blockHash,16)):
                    return False
        return True
    except sqlite3.IntegrityError:
        print("query failed.")

def getLastBlock():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select * from localChains where id = (select max(id) from localChains)')
    query = cursor.fetchone()
    db.close()
    if(query):
        return dbtoBlock(query)
    else:
        None
   
def getAllKnowChains():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        cursor.execute('select * from localChains t1 where deny = 0 and not exists (select prev_hash from localChains t2 where t1.hash = t2.prev_hash) group by idChain')
        queries = cursor.fetchall()
        db.close()
        return queries
       
    except sqlite3.IntegrityError:
        print("getAllKnowBlock Error")

def updateBlock(lastTimeTried,hash):
    try:
        db = sqlite3.connect(databaseLocation)
        cursor = db.cursor()
        cursor.execute("update localChains set lastTimeTried = '%s' where hash='%s'" %(lastTimeTried,hash))
        db.commit()
        db.close()
    except sqlite3.IntegrityError:
        print("Update block error")

def blockIsLeaf(blockIndex, blockPrevHash): 
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("select * from localChains where id = %d" % blockIndex)
    queries = cursor.fetchall()
    db.close()
    if queries:
        for query in queries:
            prev_hash = query[3]
            if(prev_hash == blockPrevHash):
                return False
    return True
    
def createNewChain(block):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select max(idChain) from localChains')
    query = cursor.fetchone()
    db.close()
    if query[0]:
        writeChainLeaf(int(query[0]) + 1, block)        
    else:
        writeChainLeaf(1, block)
    return True

def blockIsMaxIndex(blockIndex):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("select * from localChains where id = %d" % blockIndex)
    queries = cursor.fetchall()
    db.close()
    if queries:
        return False
    else:
        return True

def removeAllBlocksHigh(blockIndex,blockRound):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('select distinct(idChain) from localChains')
    queries = cursor.fetchall()
    status = False
    if(queries):
        for query in queries:
            cursor.execute('select * from localChains where id = %d and idChain = %d' %(blockIndex,query[0]))
            bquery = cursor.fetchone()
            if(bquery):
                if(bquery[2] > blockRound):
                    cursor.execute('delete * from localChains where id >= %d' %(bquery[1]))
                    db.commit()
                    status = True
        db.close()
    else:
        return status
    
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

def blockHashQuery(hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" % hash)
    b = cursor.fetchone()
    db.close()
    return b

def removeBlock(hash):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % hash)
    query = cursor.fetchone()
    if(query):
        if(query[0] == 0):
            cursor.execute("DELETE FROM localChains WHERE hash = '%s'" % hash)
    db.commit()
    db.close()

def removeChain(blockHash):
    removedBlocks = {}
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT id, prev_hash, fork, arrive_time from localChains where hash = '%s'" % blockHash)
    query = cursor.fetchone()
    if(query):
        startForkTime = query[3]
        startForkBlock = query[0]
        endForkTime = int(time.mktime(datetime.datetime.now().timetuple()))
        endForkBlock = query[0]
    hash = blockHash
    i = 1
    while(query):
        fork = query[2]
        if(int(fork) == 0):
            removedBlocks[i] = []
            removedBlocks[i].append(hash) 
            #cursor.execute("DELETE FROM localChains where hash = '%s'" % hash)
            #db.commit()
            startForkTime = query[3]
            startForkBlock = query[0]
        else:
            if(fork > 0):
                fork = fork - 1
            else:
                fork = 0
            cursor.execute("UPDATE localChains set fork = %d where hash = '%s'" % (fork,hash))
            db.commit()
            setLogFork(startForkBlock, endForkBlock, startForkTime, endForkTime)
            i = len(removedBlocks)
            while i >= 1:
                hash = removedBlocks[i][0]
                print("hash removed")
                print(hash)
                cursor.execute("UPDATE localChains set deny = 1 where hash = '%s'" % hash)
                #cursor.execute("DELETE FROM localChains where hash = '%s'" % hash)
                db.commit()
                i = i - 1
            db.close()
            return True

        i = i + 1    
        hash = query[1]
        cursor.execute("SELECT id, prev_hash, fork, arrive_time from localChains where hash = '%s'" % hash)
        query = cursor.fetchone()
    db.close()
    return False
        
def removeLeafChain(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT max(id), hash, fork, arrive_time from localChains where leaf_head = '%s' and fork <> 0" % messages[1])
    query = cursor.fetchone()
    print("QUERY")
    print(query)

    if(query[0]):
        ###insert log_fork
        firstId = int(query[0] + 1)
        cursor.execute("SELECT * from localChains where leaf_head = '%s' and id = %d" % (messages[1], firstId))     
        logQuery = cursor.fetchone()
        if(logQuery[0]):
            startFork = logQuery[7]
            startBlock = logQuery[0]

        cursor.execute("SELECT max(id), arrive_time from LocalChains where leaf_head = '%s'" % messages[1])
        logQuery = cursor.fetchone()
        if(logQuery[0]):
            endBlock = logQuery[0]
            endFork = int(time.mktime(datetime.datetime.now().timetuple()))

        setLogFork(startBlock, endBlock, startFork, endFork)
        ###end log fork
        

        ###start remove chain 
            
        block_hash = query[1]
        fork = query[2]
        print("Fork")
        print(fork)
        fork = int(fork) - 1
        cursor.execute("DELETE FROM localChains where leaf_head = '%s' and id > (SELECT max(id) from localChains where leaf_head = '%s' and fork <> 0)" % (messages[1],messages[1]))
        cursor.execute("UPDATE localChains set fork = %d where hash = '%s' " % (fork, block_hash))
        db.commit()
        #return True
       
    else:
        print("REMOVE ALL CHAIN")
        print("HEAD")
        print(messages[1])
        #remove all chain.
        cursor.execute("SELECT *  from localChains where id = (SELECT min(id) from localChains where leaf_head = '%s')" % messages[1])
        query = cursor.fetchone()
        if(query):

            ###start insert fork on log_fork
            startFork = query[7]
            startBlock = query[0]

            cursor.execute("SELECT max(id) from LocalChains where leaf_head = '%s'" % messages[1])
            logQuery = cursor.fetchone()
            if(logQuery[0]):
                endBlock = logQuery[0]
                endFork = int(time.mktime(datetime.datetime.now().timetuple()))

            setLogFork(startBlock, endBlock, startFork, endFork)
            ###end insert fork on log_fork

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
            if(query):
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
                        if(query):
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
            #return True

        #else:
        #    return False



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
    
   
def dbCheckChain(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    blocks = defaultdict(list)
    blocks_orde = defaultdict(list)
    #cursor.execute("SELECT id,leaf_head FROM localChains WHERE hash ='%s'" % messages[0])
    #query = cursor.fetchone()
    #prefixHead = ''
    #prefixId = None
    #if(query):
    #    prefixId = query[0]
    #    prefixHead = query[1]

    #cursor.execute("SELECT id,leaf_head FROM localChains WHERE hash ='%s'" % messages[1])
    #query = cursor.fetchone()
    #sufixHead = None
    #sufixId = None
    #if(query):
    #    sufixId = query[0]
    #    sufixHead = query[1]

    #query = None
    #if(prefixHead == sufixHead):
    #    print("Same Chain")
    #    cursor.execute("SELECT * FROM localChains WHERE id > %d and leaf_head = '%s' order by id asc " % (prefixId, prefixHead))
    #    query = cursor.fetchall()
    #    db.close()
    #    return query
    hash = messages[0]
    k = 0
    print("ULTIMO HASH CONHECIDO")
    print(hash)
    print("HASH RECEBIDO DO FUTURO")
    print(messages[1])
    while (hash):
        cursor.execute("SELECT * FROM localChains WHERE prev_hash = '%s'" % hash)
        query = cursor.fetchone()
        if(query):
            hash = query[3]
            print("PROXIMO HASH")
            print(hash)
            blocks[k].append(query)
            if(hash == messages[1]):
                return pickle.dumps(blocks)
            k = k + 1
        else:
            return None

       
        
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
        return block.Block(b[1],b[3],b[2],b[5],b[8],b[4],b[7],b[11],b[12])
 
def getLastBlockIndex():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT MAX(id) FROM chain')
    l = cursor.fetchone()
    l = int(l[0])
    db.close()
    return l

def quantityofBlocks(lastBlockSimulation):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM localChains WHERE stable = 1 and id > '%d'" % (lastBlockSimulation))
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
