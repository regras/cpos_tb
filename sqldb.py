#!/usr/bin/env python
import sqlite3
import logging
from block import Block
import block
from block import Block
from testedb import Transaction
import blockchain
import leaf
import parameter
import datetime
import time
import hashlib
from collections import deque, Mapping, defaultdict
import pickle
import math
import mysql.connector
import chaincontrol
from decimal import Decimal
from random import randint
logger = logging.getLogger(__name__)
#txdatabaseLocation = 'blocks/transaction.db'
databaseLocation = 'blocks/blockchain.db'




# write methods work with block objects instead of tuple from sqlite db
def connect():
    try:
        db = sqlite3.connect(databaseLocation,timeout=20,check_same_thread=False)
        cursor = db.cursor()
    except Exception as e:
        print(str(e))
    return db

def myconnect():
    try:
        db = mysql.connector.connect(user='root', password='root', host='localhost', auth_plugin='mysql_native_password', connect_timeout=20)
        cursor = db.cursor()
    except Exception as e:
        print(str(e))
    return db

def mydbConnect():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
        id integer(32) NOT NULL,
        round integer,
        prev_hash text,
        hash VARCHAR(256) NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id, hash))""")
    

    cursor.execute("""CREATE TABLE IF NOT EXISTS chain (
        id integer(32) NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id))""")
        
    cursor.execute("""CREATE TABLE IF NOT EXISTS localChains (
        idChain integer(32) NOT NULL,
        id integer(32) NOT NULL,
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
        proof_hash text,
        numSuc integer,
        round_stable integer default 0,
        PRIMARY KEY (id,idChain))""")
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS block_transaction (
        tx_hash VARCHAR(256) NOT NULL,
        block_hash VARCHAR(256) NOT NULL,
        block_round integer,
        PRIMARY KEY(tx_hash,block_hash))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS pool_transactions (
        tx_hash VARCHAR(256) NOT NULL,
        tx_prev_hash text NOT NULL,
        input_address text NOT NULL,
        value integer,
        output_address text NOT NULL,
        committed integer default 0,
        choosen integer default 0,
        block_hash text NOT NULL,        
        PRIMARY KEY (tx_hash))""")
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS utxo_set (
        tx_hash VARCHAR(256) NOT NULL,
        output_address text NOT NULL,
        value integer,
        PRIMARY KEY(tx_hash))""")

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
      id INTEGER PRIMARY KEY AUTO_INCREMENT,
      startBlock integer default 0,
      endBlock integer default 0,
      startFork text,
      endFork text)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS transmit_block (
      idAutoNum INTEGER PRIMARY KEY AUTO_INCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash text,
      proof_hash text,
      tx text,
      status integer,
      subuser integer)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS arrived_block (
      idAutoNum INTEGER PRIMARY KEY AUTO_INCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash varchar(256),
      proof_hash text,
      tx text,
      status integer,
      subuser integer,
      create_time text,
      UNIQUE (hash))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS log_block (
      idAutoNum INTEGER PRIMARY KEY AUTO_INCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash varchar(256),
      proof_hash text,
      tx text,
      status integer,
      subuser integer,
      UNIQUE (hash))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS reversion (
      id INTEGER(32) NOT NULL,
      sround INTEGER NOT NULL,
      endround INTEGER NOT NULL,      
      PRIMARY KEY (id))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS block_reversion (
      idreversion INTEGER(32) NOT NULL,
      idrevblock INTEGER(32),
      roundrevblock INTEGER,
      hashrevblock TEXT,
      rconfirmation INTEGER,
      PRIMARY KEY (idreversion,idrevblock))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions_cache (
        hash_transaction	varchar(256) NOT NULL,
    	taxa	FLOAT DEFAULT 0,
        taxabyte FLOAT DEFAULT 0,
    	payload_lenght	INTEGER NOT NULL,
    	payload	TEXT NOT NULL,
        source_address	TEXT NOT NULL,
	    destination_address	TEXT NOT NULL,
	    status	INTEGER NOT NULL,
    	PRIMARY KEY(hash_transaction)
        )""")  

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions_block (
        hash_block	VARCHAR(256) NOT NULL,
        hash_transaction	VARCHAR(256)NOT NULL,
        taxa	FLOAT DEFAULT 0,
    	payload_lenght	INTEGER NOT NULL,
    	payload	TEXT NOT NULL,
        source_address	TEXT NOT NULL,
	    destination_address	TEXT NOT NULL,
    	PRIMARY KEY(hash_transaction,hash_block)
        )""")  

    db.commit()
    cursor.close()
    db.close()

mydbConnect

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
        proof_hash text,
        numSuc integer,
        round_stable integer default 0,
        PRIMARY KEY (id,idChain))""")
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS block_transaction (
        tx_hash text NOT NULL,
        block_hash text NOT NULL,
        block_round integer,
        PRIMARY KEY(tx_hash,block_hash))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS pool_transactions (
        tx_hash text NOT NULL,
        tx_prev_hash text NOT NULL,
        input_address text NOT NULL,
        value integer,
        output_address text NOT NULL,
        committed integer default 0,
        choosen integer default 0,
        block_hash text NOT NULL default 0,        
        PRIMARY KEY (tx_hash))""")
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS utxo_set (
        tx_hash text NOT NULL,
        output_address text NOT NULL,
        value integer,
        PRIMARY KEY(tx_hash))""")

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
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS transmit_block (
      idAutoNum INTEGER PRIMARY KEY AUTOINCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash text,
      proof_hash text,
      tx text,
      status integer,
      subuser integer)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS arrived_block (
      idAutoNum INTEGER PRIMARY KEY AUTOINCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash text,
      proof_hash text,
      tx text,
      status integer,
      subuser integer,
      create_time text,
      UNIQUE (hash))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS log_block (
      idAutoNum INTEGER PRIMARY KEY AUTOINCREMENT,
      id INTEGER NOT NULL,
      round integer,
      arrive_time text,
      node text,
      prev_hash text,
      hash text,
      proof_hash text,
      tx text,
      status integer,
      subuser integer,
      UNIQUE (hash))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS reversion (
      id INTEGER NOT NULL,
      sround INTEGER NOT NULL,
      endround INTEGER NOT NULL,      
      PRIMARY KEY (id))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS block_reversion (
      idreversion INTEGER NOT NULL,
      idrevblock INTEGER,
      roundrevblock INTEGER,
      hashrevblock TEXT,
      rconfirmation INTEGER,
      PRIMARY KEY (idreversion,idrevblock))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions_cache (
        hash_transaction	TEXT NOT NULL,
    	taxa	REAL DEFAULT 0,
        taxabyte REAL DEFAULT 0,
    	payload_lenght	INTEGER NOT NULL,
    	payload	TEXT NOT NULL,
        source_address	TEXT NOT NULL,
	    destination_address	TEXT NOT NULL,
	    status	INTEGER NOT NULL,
    	PRIMARY KEY(hash_transaction)
        )""")  

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions_block (
        hash_block	TEXT NOT NULL,
        hash_transaction	TEXT NOT NULL,
        taxa	REAL DEFAULT 0,
    	payload_lenght	INTEGER NOT NULL,
    	payload	TEXT NOT NULL,
        source_address	TEXT NOT NULL,
	    destination_address	TEXT NOT NULL,
    	PRIMARY KEY(hash_transaction,hash_block)
        )""")  

    db.commit()
    db.close()
       
def insertnewtx(transaction):
    try:
        print(id)
        taxabyte = transaction.taxabyte
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("""INSERT INTO transactions_cache (hash_transaction,taxa,taxabyte,payload_lenght,payload,source_address,destination_address,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (transaction.id_hash, transaction.tax, taxabyte, transaction.payloadsize, transaction.payload, transaction.source, transaction.destination, 0))
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))



def selecttx(maxsize):
    try:
        bsize=0
        blocktx=[]
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM transactions_cache WHERE status=0 ORDER BY taxabyte DESC")
        queries =  cursor.fetchall()
        for query in queries:
            tx = Transaction(query[0],query[4],query[3],query[1])
            if (bsize + tx.payloadsize) <= maxsize:
                blocktx.append(tx)
                bsize = bsize + tx.payloadsize
        return blocktx
    except Exception as e:
        print(str(e))

def copymempool():
    try:
        tx=[]
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM transactions_cache WHERE status=0 ORDER BY taxabyte DESC")
        queries =  cursor.fetchall()
        for query in queries:
            tx.append(Transaction(query[0],query[4],query[3],query[1]))
        return tx
    except Exception as e:
        print(str(e))



def updatetxstatus(idhash,status):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("""UPDATE transactions_cache
            SET status=%s 
            WHERE hash_transaction = %s
            """, (status,idhash))
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))

def removefbtx():
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("DELETE from transactions_cache WHERE status = 2")
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))

def removetx(transaction):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("DELETE from transactions_cache WHERE hash_transaction = %s", (transaction.id_hash,))
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))

def txinblock(transaction,block):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute('INSERT INTO transactions_block (hash_block,hash_transaction,taxa,payload_lenght,payload,source_address,destination_address) VALUES (%s,%s,%s,%s,%s,%s,%s)',
        (block.hash,transaction.id_hash, transaction.tax, transaction.payloadsize, transaction.payload, transaction.source, transaction.destination))
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))

def verifytxnotinblock(transaction):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions_block WHERE hash_transaction = '%s'" %(transaction.id_hash))
    tx = cursor.fetchone()
    if (tx):
        return False
    else:
        return True

def isLeaf(index):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM localChains WHERE id > %d" % index)
        query = cursor.fetchone()
        db.close()
        cursor.close()
        if query:
            return False
        else:
            return True
    except Exception as e:
        print(str(e))

    return False

def getBlockIntervalByRound(fround,lround):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM localChains where round >= %d and round <= %d order by id asc" %(fround,lround))
        queries = cursor.fetchall()
        db.close()
        cursor.close()
        return queries
    except Exception as e:
        print(str(e))

def getBlockByRound(round):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM localChains where round = %d" % round)
        b = cursor.fetchone()
        if(b):
            return(dbtoBlock(b))
        else:
            return None
    except Exception as e:
        print(str(e))
        
def getLogBlock(hash):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM log_block where hash = '%s'" % (hash))
        b = cursor.fetchone()
        db.close()
        cursor.close()
        if(b):            
            return(block.Block(b[1],b[5],b[2],b[4],b[3],b[6],b[8],b[10],b[7]))
        else:
            return None
    except Exception as e:
        print(str(e))
    
def checkSyncChain(lround,round):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        queries = None
        #blockchain = {}
        s = {}
        #sr_0 = chaincontrol.calcZr(None,0)
        cursor.execute("SELECT * FROM localChains WHERE stable = 0 AND round > %d and round < %d ORDER BY id ASC" %(lround, (round - parameter.roundTolerancy)))
        #cursor.execute("SELECT * from localChains where stable = 0 and id = (select min(id) from localChains where stable = 0) order by id asc")
        #query = cursor.fetchone()
        queries = cursor.fetchall()
        #if(query):
        status = True
        for query in queries:
            if(status):
                status = False
                #index_round = round - 1
                index_round = (round - parameter.roundTolerancy) - 1
                cursor.execute("SELECT * FROM localChains t1 WHERE t1.id = (SELECT MAX(id) FROM localChains WHERE round > %d AND round < %d)" %(lround, (round - parameter.roundTolerancy)))
                #cursor.execute("SELECT * from localChains t1 where not exists (select * from localChains t2 where t2.prev_hash = t1.hash)")
                item = cursor.fetchone()
                while(item[1] >= query[1] and (index_round - int(query[2]) > 1)):
                    #print("index block atual: %d" %int(query[1]))
                    #print("index block variando: %d" %int(item[1]))                
                    while(index_round > int(item[2])):
                        #z[index_round] = zr_0
                        s[index_round] = 0
                        index_round = index_round - 1

                    if(index_round == int(item[2] and item[1] > query[1])):
                        #zr = chaincontrol.calcZr(item[12],item[13])
                        #z[index_round] = zr
                        s[index_round] = item[13]
                        index_round = index_round - 1

                    #time.sleep(0.5)
                    cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" %item[3])
                    item = cursor.fetchone()
            
    
    except Exception as e:
        print(str(e))

def getCurrentSuc(lround,round):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        s = 0
        cursor.execute("SELECT * FROM localChains where round >= %d and round <= %d" %(int(lround),int(round)))
        queries = cursor.fetchall()
        if queries:
            for query in queries:
                s = s + int(query[13])
        db.close()
        cursor.close()
        return s
    except Exception as e:
        print(str(e))
        

def reversionBlock(round, lround, commit, db = None):
    try:
        if(not db):
            db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        queries = None
        #blockchain = {}
        s = {}
        #sr_0 = chaincontrol.calcZr(None,0)
        cursor.execute("SELECT * FROM localChains WHERE stable = 0 AND round > %d and round < %d ORDER BY id ASC" %(lround, (round - parameter.roundTolerancy)))
        #cursor.execute("SELECT * from localChains where stable = 0 and id = (select min(id) from localChains where stable = 0) order by id asc")
        #query = cursor.fetchone()
        queries = cursor.fetchall()
        #if(query):
        status = True
        if(queries):
            for query in queries:
                if(status):
                    status = False
                    #index_round = round - 1
                    index_round = (round - parameter.roundTolerancy) - 1
                    cursor.execute("SELECT * FROM localChains t1 WHERE t1.id = (SELECT MAX(id) FROM localChains WHERE round < %d)" %((round - parameter.roundTolerancy)))
                    #cursor.execute("SELECT * from localChains t1 where not exists (select * from localChains t2 where t2.prev_hash = t1.hash)")
                    item = cursor.fetchone()
                    while(item[1] >= query[1] and (index_round - int(query[2]) >= 1)):
                        #print("index block atual: %d" %int(query[1]))
                        #print("index block variando: %d" %int(item[1])) 
                        print("query hash: ", query[4])
                        print("lround: ", lround)
                        print("item[2]: ", item[2])            
                        print("index_round: ", index_round)  
                        print("item[1]: ", item[1])
                        print("query[1]: ", query[1])
                        while(index_round > int(item[2])):
                            print("index_round > int(item[2])")
                            #z[index_round] = zr_0
                            s[index_round] = 0
                            index_round = index_round - 1

                        if(index_round == int(item[2]) and (item[1] > query[1])):
                            #zr = chaincontrol.calcZr(item[12],item[13])
                            #z[index_round] = zr
                            print("index_round == int(item[2])")
                            s[index_round] = item[13]
                            index_round = index_round - 1

                        #time.sleep(0.5)
                        cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" %item[3])
                        item = cursor.fetchone()
                        if not item:
                            db.close()
                            cursor.close()
                            return lround, False, commit

                deltar = (round - parameter.roundTolerancy) - query[2]
                print("s: ",s)
                print("deltar: ",deltar)
                if(deltar >= 2):            
                    check,sync = chaincontrol.checkcommitted(s,deltar)
                    if(check):
                        lround = query[2]
                        cursor.execute("UPDATE localChains set stable = 1, round_stable = %d where hash = '%s'" %((round - parameter.roundTolerancy - 1),query[4]))
                        db.commit()
                        print("BLOCK INDEX %d COMMITED" %query[1])
                        commit = query[1]
                    else:
                        if(not sync):
                            db.close()
                            cursor.close()
                            return  lround, False, commit
                        else:
                            break
                else:
                    break
                del s[query[2] + 1]
            db.close()
            cursor.close()
            return lround,True, commit
        else:
            if(round - lround > 1):
                db.close()
                cursor.close()
                return lround, False, commit
        db.close()
        cursor.close()
        return lround, True, commit

    except Exception as e:
        print(str(e))
        
def getLastStableBlock(lastBlockSimulation):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT max(id) FROM localChains WHERE id > '%d'" % lastBlockSimulation)
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return query[0]
    else:
        return None

####functions to sync
def getHead(blockHash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT leaf_head from localChains WHERE hash = '%s'" % blockHash)
    query = cursor.fetchone()
    if(query):
        db.close()
        cursor.close()
        return query[0]
    else:
        db.close()
        cursor.close()
        return None

def verifyBlockIsLeaf(blockHash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT hash from localChains WHERE prev_hash = '%s' limit 1" % blockHash)
    query = cursor.fetchone()
    if(query):
        db.close()
        cursor.close()
        return False
    else:
        db.close()
        cursor.close()
        return True
    
def verifyRoundBlock(blockId,blockRound):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    cursor.execute("SELECT round from localChains WHERE id = %d limit 1" % blockId)
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        print("VERIFIED ROUND BLOCK: ", query[0])
        print("NEW BLOCK ROUND: ", blockRound)
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
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
                cursor.close()
                return True
            else:
                blockHash = query[0]
                difIndex = difIndex - 1
        else:
            db.close()
            cursor.close()
            return False
    db.close()
    cursor.close()
    return False

def knowLogBlock(hash):
    try: 
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM arrived_block WHERE hash = '%s'" % hash)
        query = cursor.fetchone()
        db.close()
        cursor.close()   
        #print("QUERY: ", query)         
        if(query):
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False

def dbKnowBlock(hash):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        cursor.execute("SELECT * from localChains WHERE hash = '%s'" % hash)
        query = cursor.fetchone()
        if(query):
            db.close()
            cursor.close()
            return True
        else:
            db.close()
            cursor.close()
            return False
    except Exception as e:
        print(str(e))
        return False

def dbReqBlock(messages):
    try:
        role = messages[1]
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        if(role == 'majorblock'):
            r = messages[0]
            r = int(pickle.loads(r))
            cursor.execute("SELECT * from localChains where id = (SELECT max(id) from localChains where round <= %d)" % r)
            query = cursor.fetchone()
            db.close()
            cursor.close()
            if(query):
                return pickle.dumps(dbtoBlock(query),2)
            else:            
                return None

        elif(role == 'allblocks'):
            b = messages[0]
            b = pickle.loads(b)
            blocks = []
            cursor.execute("SELECT * from log_block where prev_hash = '%s' and round = %d" %(b.prev_hash,b.round))
            queries = cursor.fetchall()
            db.close()
            cursor.close()
            if(queries):
                for query in queries:
                    blocks = blocks + [block.Block(query[1],query[5],query[2],query[4],query[3],query[6],query[8],query[10],query[7])]
                return pickle.dumps(blocks,2)
            return None

        elif(role == 'block'):
            hash = messages[0]
            hash = pickle.loads(hash)
            return pickle.dumps(getLogBlock(hash),2)

    except Exception as e:
        print(str(e))
    return None

#####end functions to sync

def bournChain(head):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT min(id) FROM localChains WHERE leaf_head = '%s'" % head)
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return query[0]
    else:
        return None

def getPrev3Block(hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT round, prev_hash, arrive_time FROM localChains WHERE hash = '%s'" % hash)
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return query
    else:
        return None

    
def checkActiveFork(numBlocks):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM log_fork WHERE startBlock > %d and status = 1" % (numBlocks)) 
    queries = cursor.fetchall()
    db.close()
    cursor.close()
    if(queries):
        return True
    else:
        return False

def getBlock(hash=None):    
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    try:
        if(hash):
            cursor.execute("SELECT * from localChains where hash = '%s'" % hash)       
        else:
            cursor.execute("SELECT * from localChains t1 where not exists(SELECT * from localChains t2 where t1.hash = t2.prev_hash)")      
        query = cursor.fetchone()
        if(query):
            db.close()
            cursor.close()
            return dbtoBlock(query)
    except Exception as e:
        print(str(e))
    db.close()
    cursor.close()
    return None

def getBlocks(numBlocks):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * from log_block WHERE idAutoNum > %d" % (numBlocks))
    queries = cursor.fetchall()
    db.close()
    cursor.close()
    return queries

def dbNumBlocks(numBlocks):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) from log_block WHERE idAutoNum > %d" % (numBlocks))
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return query[0]
    else:
        return None

def getForks(lastForks):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    cursor.close()
    print("sendQueries")
    print(sendQueries)
    return sendQueries

def dbNumForks():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) from log_fork")
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return query[0]
    else:
        return None

def hasDb(hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT hash from localChains WHERE hash = '%s'" % hash)
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if query:
        return True
    else:
        return False

def setStableBlocks(round):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    round = round - parameter.roundTolerancy
    cursor.execute("SELECT hash from localChains t1 WHERE EXISTS (SELECT hash FROM localChains t2 WHERE t1.id = t2.id GROUP BY id HAVING COUNT(*) = 1) and stable = 0")
    queries = cursor.fetchall()
    if queries:
        for query in queries:
            cursor.execute("UPDATE localChains set stable = 1 WHERE round < %d AND stable = 0 AND hash = '%s'" % (round, query[0]))
            db.commit()
    cursor.execute("SELECT COUNT(*) FROM localChains WHERE stable = 1")
    queries = cursor.fetchone()
    if queries:
        stableBlocks = queries[0]

    db.commit()
    db.close()
    cursor.close()
    return stableBlocks

#def setLogFork(head, localtime, status, startIndex = 0, endIndex = 0, leaf_hash = None, hash1 = None, hash2 = None):
def setLogFork(startBlock, endBlock, startFork, endFork):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    #if(status == 1):
    print("ENTROU SETLOGFORK")
    cursor.execute('INSERT INTO log_fork (startBlock, endBlock, startFork, endFork) VALUES (%s,%s,%s,%s)',(
    startBlock,
    endBlock,
    startFork,
    endFork))
    db.commit()
    db.close()
    cursor.close()
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
def changeArrivedBlock(b,accepted):
    if(b):
        try:
            db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
            cursor = db.cursor()
            cursor.execute("UPDATE arrived_block set status = %d where hash = '%s'" %(accepted, b.hash))
            db.commit()
            db.close()
            cursor.close()
        except Exception as e:
            print(str(e)) 

def setArrivedBlock(b,accepted,db=None):    
    if(b):
        try:
            if not db:
                db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
            cursor = db.cursor()
            cursor.execute("SELECT * from arrived_block where hash = '%s'" %b.hash)
            query = cursor.fetchone()
            if(not query):
                cursor.execute('INSERT INTO arrived_block (id, round, arrive_time, node, prev_hash, hash,proof_hash,tx,status,subuser,create_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['arrive_time'],
                    b.__dict__['node'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['proof_hash'],
                    b.__dict__['tx'],
                    accepted,
                    b.__dict__['subuser'],
                    b.__dict__['create_time']))
                db.commit()
            db.close()
            cursor.close()
        except mysql.connector.IntegrityError:
            logger.warning('db insert duplicated block on arrived_block')

def setTransmitedBlock(b,accepted,db=None):
    if(b):
        if(not db):
            db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        try:            
            cursor.execute('INSERT INTO transmit_block (id, round, arrive_time, node, prev_hash, hash,proof_hash,tx,status,subuser) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(
                b.__dict__['index'],
                b.__dict__['round'],
                b.__dict__['arrive_time'],
                b.__dict__['node'],
                b.__dict__['prev_hash'],
                b.__dict__['hash'],
                b.__dict__['proof_hash'],
                b.__dict__['tx'],
                accepted,
                b.__dict__['subuser']))
            db.commit()
            db.close()
            cursor.close()
        except mysql.connector.IntegrityError:
            logger.warning('db insert duplicated block on transmit_block')

def setLogBlock(b, accepted):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    if(b):
        try:
            cursor.execute("SELECT * from log_block where hash = '%s'" %b.hash)
            query = cursor.fetchone()
            if(not query):                
                cursor.execute('INSERT INTO log_block (id, round, arrive_time, node, prev_hash, hash,proof_hash,tx,status,subuser) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['arrive_time'],
                    b.__dict__['node'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['proof_hash'],
                    b.__dict__['tx'],
                    accepted,
                    b.__dict__['subuser']))
                db.commit()
                #update LocalChain if received block proof_hash is different of localChain proof_hash
                cursor.execute('SELECT * from localChains where round = %d' %b.round)
                query=cursor.fetchone()
                if(query):
                    if(query[4] != b.hash and b.prev_hash == query[3]):                        
                        suc = query[13] + b.subuser
                        cursor.execute("UPDATE localChains set numSuc = %d where hash = '%s'" %(suc,query[4]))
                        db.commit()

        except mysql.connector.IntegrityError:
            logger.warning('db insert duplicated block on log_block')
        finally:         
            db.close()
            cursor.close() 

#def setLogMine(l, b):
#    db = sqlite3.connect(databaseLocation)
#    cursor = db.cursor()

#    try:
       #print("HEAD NOVO BLOCO")
       #print(l.leaf_head)     
#        cursor.execute('INSERT INTO log_mine VALUES (%s,%s,%s)',(
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
#    cursor.execute('INSERT INTO log_mine VALUES (%s,%s,%s)', (
#                    b.__dict__['hash'],
#                    b.__dict__['arrive_time'],
#                    l.__dict__['leaf_head']))
#    db.commit()
#    db.close()


def setForkFromBlock(block_hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    query = cursor.fetchone()

    if(query):
        forks = query[0]
        forks = int(forks) + 1
        cursor.execute("UPDATE localChains SET fork = %d WHERE hash = '%s'" % (forks, block_hash))

    db.commit()
    db.close()
    cursor.close()

def clearForkFromBlock(block_hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    query = cursor.fetchone()
    forks = query[0]
    if(int(forks) > 0):
        forks = int(forks) - 1
        cursor.execute("UPDATE localChains SET fork = '%s' WHERE hash = '%s'" % (forks, block_hash))
    db.commit()
    db.close()
    cursor.close()

def checkForkFromBlock(block_hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT fork FROM localChains WHERE hash = '%s'" % block_hash)
    forks = cursor.fetchone()
    db.commit()
    db.close()
    cursor.close()
    return int(forks)

def dbCheck():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    cursor.close()
    return bc

def checkChainIsLeaf(leaf_db):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('select * from localChains')
    leafs_db = cursor.fetchall()
    if not leafs_db:
        b = block.Block(index=0,prev_hash="",round=0,node="",b_hash="",arrive_time=parameter.GEN_ARRIVE_TIME)
        createNewChain(b,0)
    db.commit()
    db.close()
    cursor.close()
    return True
    
def writeBlock(b):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()

    try:
        if isinstance(b, list):
            cursor.executemany('INSERT INTO blocks VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', b)
        else:
            cursor.execute('INSERT INTO blocks VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except mysql.connector.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()
        cursor.close()

def writeChainLeaf(idChain,b,firstBlock=False,db=None):
    if(not db):
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    try:
        #update subUser on localChain Block if this block is other block on round r
        cursor.execute("SELECT * from log_block where round = %d and prev_hash = '%s'" %(b.round, b.prev_hash))
        queries = cursor.fetchall()
        suc = 0
        if(queries):
            for query in queries:
                suc = suc + query[10]        
        #suc = suc + subUser
        if(firstBlock):
            stable = 1
        else:
            stable = 0   
        cursor.execute('INSERT INTO localChains VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
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
                stable,
                b.__dict__['subuser'],
                b.__dict__['proof_hash'],
                suc,
                '0'))
        db.commit()
       
    except mysql.connector.IntegrityError:
        logger.warning('db insert duplicated block in the same chain')
    #finally:
    #    db.close()cursor.close()
def getIdChain(blockHash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    try:
        cursor.execute("select idChain from localChains where hash = '%s'" %blockHash)
        query = cursor.fetchone()
        db.close()
        cursor.close()
        if(query):
            return query[0]
        else:
            return None
    except mysql.connector.IntegrityError:
        print("impossible to return chain id")

def blockIsPriority(blockIndex,proof_hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    try:
        cursor.execute('select proof_hash from localChains where id = %d' %blockIndex)
        queries = cursor.fetchall()
        db.close()
        cursor.close()
        if(queries):
            for query in queries:
                if(int(query[0],16) <= int(proof_hash,16)):
                    return False
        return True
    except mysql.connector.IntegrityError:
        print("query failed.")

def getLastBlock():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('select * from localChains where id = (select max(id) from localChains)')
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if(query):
        return dbtoBlock(query)
    else:
        None
   
'''def getAllKnowChains():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    blocks = {}
    try:
        cursor.execute('select distinct(idChain) from localChains')
        queries = cursor.fetchall()
        if(queries):
            for query in queries:
                cursor.execute('select * from localChains where id = (select max(id) from localChains) and idChain = %d' % query[0])
                bquery = cursor.fetchone()
                if(bquery):
                    if(blocks):
                        i = max(blocks) + 1
                    else:
                        i = 0
                    blocks[i] = []
                    blocks[i] = blocks[i] + [dbtoBlock(bquery)]
                    print(blocks)
                    
            db.close()
            return blocks
       
    except sqlite3.IntegrityError:
        print("getAllKnowBlock Error")'''
        
def getAllKnowChains():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    #blocks = {}
    try:
        cursor.execute('select * from localChains where id = (select max(id) from localChains)')
        #cursor.execute('select * from localChains t1 where not exists(select prev_hash from localChains t2 where t1.hash == t2.prev_hash) group by t1.idChain')
        query = cursor.fetchone()
        if(query):
            return dbtoBlock(query)
        else:
            return None
    except mysql.connector.IntegrityError:
        print("getAllKnowBlock Error")

def updateBlock(lastTimeTried,hash):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute("update localChains set lastTimeTried = '%s' where hash='%s'" %(lastTimeTried,hash))
        db.commit()
        db.close()
        cursor.close()
    except mysql.connector.IntegrityError:
        print("Update block error")

def blockIsLeaf(blockIndex, blockPrevHash): 
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    index = blockIndex + 1
    cursor.execute("select * from localChains where id = %d" % index)
    queries = cursor.fetchall()
    db.close()
    cursor.close()
    if queries:
        for query in queries:
            prev_hash = query[2]
            if(prev_hash == hash):
                return False
    return True
    
def createNewChain(block,subUser):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('select max(idChain) from localChains')
    query = cursor.fetchone()
    db.close()
    cursor.close()
    if query[0]:
        writeChainLeaf(int(query[0]) + 1, block)        
    else:
        writeChainLeaf(1, block,firstBlock=True)
    return True

def blockIsMaxIndex(blockIndex):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    cursor.execute("select * from localChains where id = %d" % blockIndex)
    queries = cursor.fetchall()
    db.close()
    cursor.close()
    if queries:
        return False
    else:
        return True

def removeAllBlocksHigh(blockIndex,hash,db=None):
    if (not db):
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
    cursor = db.cursor()
    try:    
        cursor.execute("delete from localChains where id >= %d and hash <> '%s'" %(blockIndex, hash))
        db.commit()
        db.close()
        cursor.close()
        return True
    except mysql.connector.IntegrityError:
        print("remove from localChains error")    
    db.close()
    cursor.close()
    return False

def writeChain(b):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    try:
        if isinstance(b, list):
            cursor.executemany('INSERT INTO chain VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', b)
        else:
            cursor.execute('INSERT INTO chain VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except mysql.connector.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()
        cursor.close()

def replaceChain(b):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    print('BLOCK TO INSERT OR REPLACE ON CHAIN TABLE', b)
    try:
        if isinstance(b, tuple):
            cursor.execute('REPLACE INTO chain VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', b)
        else:
            cursor.execute('INSERT OR REPLACE INTO chain VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    b.__dict__['index'],
                    b.__dict__['round'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['node'],
                    b.__dict__['mroot'],
                    b.__dict__['tx'],
                    b.__dict__['arrive_time']))
    except mysql.connector.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()
        cursor.close()

def forkUpdate(index):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id = {0} AND prev_hash = (SELECT hash FROM chain WHERE id = {1})'.format(index,index-1))
    b = cursor.fetchone()
    #cursor.execute('REPLACE INTO chain VALUES (%s,%s,%s,%s,%s,%s,%s)', b)
    db.close()
    cursor.close()
    return b


def blockQueryFork(messages):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id = %s', (messages[1],))
    b = cursor.fetchall()
    db.close()
    cursor.close()
    return b


def blockQuery(messages):

    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id = %s', (messages[1],))
    b = cursor.fetchone()
    db.close()
    cursor.close()
    return b

def blockHashQuery(hash):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" % hash)
    b = cursor.fetchone()
    db.close()
    cursor.close()
    return b

def removeBlock(index=None,round=None,db=None):
    try:
        if(not db):
            db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        if(round):
            cursor.execute("DELETE FROM localChains WHERE round = %d" % round)            
        if(index):
            cursor.execute("DELETE FROM localChains WHERE id = %d" % index)
        db.commit()
        db.close()
        cursor.close()
    except Exception as e:
        print(str(e))

def removeChain(blockHash):
    removedBlocks = {}
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
                cursor.execute("DELETE FROM localChains where hash = '%s'" % hash)
                db.commit()
                i = i - 1
            db.close()
            cursor.close()
            return True

        i = i + 1    
        hash = query[1]
        cursor.execute("SELECT id, prev_hash, fork, arrive_time from localChains where hash = '%s'" % hash)
        query = cursor.fetchone()
    db.close()
    cursor.close()
    return False
        
def removeLeafChain(messages):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    cursor.close()
    #clearForkFromBlock(block_hash) 
    
def blocksQuery(messages):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain WHERE id BETWEEN %s AND %s', (messages[1],messages[2]))
    l = cursor.fetchall()
    db.close()
    cursor.close()
    return l

def leavesQuery():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('select * from localChains T1 where T1.id = (select max(T2.id) from localChains T2 where T1.leaf_head = T2.leaf_head group by T2.leaf_head)')
    leafs_db = cursor.fetchall()
    db.close()
    cursor.close()
    return leafs_db

def searchForkPoint(leaf):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE hash = '%s'" % leaf[2])
    leafs_db = cursor.fetchone()
    db.close()
    cursor.close()
    return leafs_db

def dbGetAllChain(messages):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM localChains WHERE leaf_head = '%s' ORDER BY id ASC" % messages[0])
    leafs_db = cursor.fetchall()
    db.close()
    cursor.close()
    return leafs_db
    
   
def dbCheckChain(messages):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
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
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    idlist = messages[1:]
    #idlist = [int(i) for i in messages[1:]]
    cursor.execute('SELECT * FROM chain WHERE id IN ({0})'.format(', '.join('?' for _ in idlist)), idlist)
    l = cursor.fetchall()
    db.close()
    cursor.close()
    return l

def dbtoBlock(b):
    """ Transform database tuple to Block object """
    if isinstance(b, block.Block) or b is None:
        return b
    else:
        return block.Block(b[1],b[3],b[2],b[5],b[8],b[4],b[7],b[11],b[12])
 
def getLastBlockIndex():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT MAX(id) FROM chain')
    l = cursor.fetchone()
    l = int(l[0])
    db.close()
    cursor.close()
    return l

def quantityofBlocks(lastBlockSimulation):
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM localChains WHERE stable = 1 and id > '%d'" % (lastBlockSimulation))
    l = cursor.fetchone()
    if l is not None:
        l = int(l[0])
    else:
        l = 0
    db.close()
    cursor.close()
    return l

def getQuantityForks():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM (SELECT COUNT(*) FROM blocks GROUP BY id HAVING COUNT(*) > 1)')
    l = cursor.fetchone()
    if l is not None:
        l = int(l[0])
    else:
        l = 0
    db.close()
    cursor.close()
    return l

def getallchain():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM chain')
    l = cursor.fetchall()
    chain = []
    for b in l:
        chain.append(dbtoBlock(b))

    db.close()
    cursor.close()
    return chain

def getallblocks():
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks')
    l = cursor.fetchall()
    tree=[]
    for b in l:
        tree.append(dbtoBlock(b))

    db.close()
    cursor.close()
    return tree

########transactions database functions##############
   
def dbAddTx(tx):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        tx = pickle.loads()
        value = tx[0][4] + tx[1][4]
        tx1 = tx[0]
        reply = False   
        status = False        
        cursor.execute("SELECT * FROM utxo_set t1 WHERE t1.tx_hash = '%s' and t1.output_address = '%s' and t1.value = %d and NOT EXISTS (SELECT * FROM pool_transaction t2 WHERE t1.tx_prev_hash = t2.tx_hash)" %(tx1[1],tx1[2],value)) 
        utxo = cursor.fetchone()
        if(utxo):
            reply = True                         
            sameTx = None
            if (len(tx) > 1):
                cursor.execute("SELECT * FROM pool_transaction WHERE tx_hash = '%s' or tx_hash = '%s'" %(tx[0][0],tx[1][0]))
            else:
                cursor.execute("SELECT * FROM pool_transaction WHERE tx_hash = '%s'" %tx[0][0])
            sameTx = cursor.fetchall()
            if(not sameTx):
                status = True        
                cursor.execute('INSERT INTO pool_transaction VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    tx1[0],
                    tx1[1],
                    tx1[2],
                    tx1[3],
                    tx1[4],
                    0,
                    0,
                    str(-1)
                ))
                db.commit()
                if(len(tx) > 1):
                    tx2 = tx[1]
                    cursor.execute('INSERT INTO pool_transaction VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                        tx2[0],
                        tx2[1],
                        tx2[2],
                        tx2[3],
                        tx2[4],
                        0,
                        0,
                        str(-1)
                    ))
                    db.commit()
        db.close()
        cursor.close()
        return reply,status  

    except Exception as e:
        print(str(e))   


def firstTransactions():
    #try:
    #creating 2000 committed transactions
    tx_hash = parameter.HASH_FIRST_TRANSACTION
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    for i in range(1,201):
        value = parameter.values[i-1]
        address = hashlib.sha256(str(i)).hexdigest()

        tx_header = str(tx_hash) + str(-1) + str(value) + str(address)    
        txh = hashlib.sha256(tx_header).hexdigest()
        cursor.execute('INSERT INTO utxo_set VALUES (%s,%s,%s)', (
            txh,
            address,
            value))
        #db.commit()
        cursor.execute('INSERT INTO pool_transactions VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
            txh,
            tx_hash,
            -1,
            value,
            address,
            1,
            1,
            parameter.HASH_FIRST_TRANSACTION))
        db.commit()     
    db.close()
    cursor.close()
  
def createtx(node_ipaddr):
    try:
        db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
        cursor = db.cursor()
        value = randint(1,100)
        cursor.execute('SELECT * FROM utxo_set t1 WHERE NOT EXISTS (SELECT * FROM pool_transactions t2 WHERE t2.tx_prev_hash = t1.tx_hash) and t1.value >= %d LIMIT 1' %value)
        query = cursor.fetchone()
        tx = None
        if(query):
            address = hashlib.sha256(str(randint(1,200))).hexdigest()
            if(query[1] != address):
                if((query[2] - value) > 0):
                    change = query[2] - value
                    tx_header = str(query[0]) + str(query[1]) + str(change) + str(query[1])            
                    tx_hash = hashlib.sha256(str(tx_header)).hexdigest()
                    '''cursor.execute('INSERT INTO pool_transactions VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    tx_hash,
                    query[0],
                    query[1],
                    change,
                    query[1],
                    0,
                    0,
                    str(-1)))
                db.commit()'''
                tx = [[tx_hash,query[0],query[1],change,query[1]]]
                tx_header = str(query[0]) + str(query[1]) + str(value) + str(address)
                tx_hash = hashlib.sha256(str(tx_header)).hexdigest()
                '''cursor.execute('INSERT INTO pool_transactions VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (
                    tx_hash,
                    query[0],
                    query[1],
                    value,
                    address,
                    0,
                    0,
                    str(-1)))
                db.commit()'''
                tx = tx + [[tx_hash,query[0],query[1],value,address]]
        db.close()
        cursor.close()
        return tx
    except Exception as e:
        print(str(e))

def insertReversion(round,lastround,db=None):
    try:
        if(not db):
            db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
        cursor = db.cursor()
        cursor.execute("SELECT max(id) from reversion")
        query = cursor.fetchone()
        if(query[0]):
            id = query[0] + 1
        else:
            id = 1       
        cursor.execute('INSERT INTO reversion VALUES (%s,%s,%s)', (
            id,
            lastround,
            round))
        db.commit()
        db.close()
        cursor.close()
        return id
    except Exception as e:
        print(str(e)) 
    return None

def addBlocksReversion(fblock,lblock,idreversion,db=None):
    try:
        if(idreversion):
            blocks = getBlockIntervalByRound(fblock.round,lblock.round)
            if(not db):
                db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password', connect_timeout=40)
            cursor = db.cursor()
            for block in blocks:
                cursor.execute('INSERT INTO block_reversion VALUES (%s,%s,%s,%s,%s)',(
                idreversion,
                block[1],
                block[2],
                block[4],
                block[14]))
                db.commit()
            db.close()
            cursor.close()
    except IntegrityError as e:
        print(str(e))

def get_trans(num):
    #try:
    reply = []
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM transmit_block WHERE id <= %d' % int(num))  
    queries = cursor.fetchone()
    if(queries):
        reply = reply + [queries[0]]
    cursor.execute('SELECT arrive_time, create_time FROM arrived_block WHERE id <= %d and status <= 2' %int(num))
    queries = cursor.fetchall()
    tavg = 0
    if(queries):
        for query in queries:
            print(query)
            print(query[1])
            tavg = tavg + (float(query[0]) - float(query[1]))
        tavg = tavg / len(queries)
        reply = reply + [tavg]
    return reply
    #except Exception as e:
    #print(str(e))
    return [None,None]


def explorer(num,node='-1'):
    receivedblocks = 0
    numround = 0
    callsync = 0
    callsyncrev = 0
    numrevblock = 0
    avgrevblock = 0
    avgconf = 0
    numblockstable = 0
    lateblocks = 0
    numblocks = 0
    numsuc = 0
    mainchainProducedBlock = 0
    allblockswithconfirmed = 0
    #try:
    db = mysql.connector.connect(user='root', password='root',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    #calculating performance
    cursor.execute("SELECT * FROM localChains WHERE stable = 1 and round <> 0")
    queries = cursor.fetchall()
    if(queries):
        numblockstable = len(queries)
        print(queries)
        for query in queries:
            #avgconf = avgconf + float(1) / float(query[14] - query[2])
            avgconf = avgconf + (float(query[14] - query[2]))
            #blocks produced on main chain
            cursor.execute("SELECT COUNT(*) FROM log_block WHERE node = '%s' and prev_hash = '%s' and round = %d and id = %d" %(node,query[3],int(query[2]),int(query[1])))
            mblocks = cursor.fetchone()
            if(mblocks):
               mainchainProducedBlock = mainchainProducedBlock + mblocks[0] 
                #print("mainchainProducedBlock: ", mainchainProducedBlock)  
            cursor.execute("SELECT COUNT(*) FROM log_block WHERE node = '%s' and id = %d" %(node,int(query[1])))         
            mblocks = cursor.fetchone()
            if(mblocks):
                allblockswithconfirmed = allblockswithconfirmed + mblocks[0]
        avgconf = avgconf / len(queries)
        
    
    #calculating performance
    cursor.execute("SELECT * FROM reversion")
    queries = cursor.fetchall()
    if(queries):
        callsync = len(queries)
        for query in queries:
            #sync[query[0],query[1],query[2]] = []
            cursor.execute("SELECT * FROM block_reversion WHERE idreversion = %d" %int(query[0]))
            revqueries = cursor.fetchall()
            if(revqueries):
                callsyncrev = callsyncrev + 1
                for revquery in revqueries:
                    numrevblock = numrevblock + 1
                    #sync[query[0],query[1],query[2]] = sync[query[0],query[1],query[2]] + [[revquery[1], revquery[2], revquery[3], revquery[4]]]       
        
    #get arrived blocks
    cursor.execute("SELECT count(*) FROM arrived_block WHERE node <> '%s'" %node)
    queries = cursor.fetchone()
    if(queries):
        receivedblocks = queries[0]

    #get produced blocks
    cursor.execute("SELECT count(*) FROM log_block WHERE node == '%s'" %node)
    queries = cursor.fetchone()
    if(queries):
        numblocks = queries[0]

    #get succesfully raffle number
    cursor.execute("SELECT sum(subuser) FROM arrived_block WHERE node == '%s'" %node)
    queries = cursor.fetchone()
    if(queries[0]):
        numsuc = queries[0]  
    
    #get rounds to produce all blocks
    cursor.execute("SELECT (max(round) - min(round)) FROM arrived_block")
    queries = cursor.fetchone()
    if(queries):
        numround = queries[0]        
            
    #late block number
    cursor.execute("SELECT COUNT(*) FROM arrived_block WHERE status = 2")
    queries = cursor.fetchone()
    if(queries):
        lateblocks = queries[0]
    
    db.close()
    cursor.close()
    #except Exception as e:
    #    print(str(e))

    return [avgconf,callsync,callsyncrev,numrevblock,receivedblocks,numround,numblockstable,lateblocks,numblocks,numsuc,mainchainProducedBlock,allblockswithconfirmed]