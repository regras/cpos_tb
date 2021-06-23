#!/usr/bin/env python
import random
import sqlite3
import logging
from block import Block
import block
from block import Block
#import blockchain
import leaf
#import parameter
import datetime
import time
import hashlib
from collections import deque, Mapping, defaultdict
import pickle
import math
#import chaincontrol
from decimal import Decimal
from random import randint
logger = logging.getLogger(__name__)
txdatabaseLocation = 'blocks/transaction.db'

avrfee = 100.0
avrsize = 600
sizedesvpad = 100

 
class Transaction:
    def __init__(self, id_hash, payload, payloadsize, tax=0, source_address='a', destination_address='b'):
        if (id_hash!='0'):
            self.id_hash = id_hash
            self.tax = tax
            self.source = source_address
            self.destination = destination_address
            self.payload = payload
            self.payloadsize = payloadsize
        else:
            print('invalid transaction')


# write methods work with block objects instead of tuple from sqlite db
def connect():
    try:
        db = sqlite3.connect(txdatabaseLocation,timeout=20,check_same_thread=False)
        cursor = db.cursor()
    except Exception as e:
        print(str(e))
    return db

def dbConnect():
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions_cache (
        hash_transaction	TEXT NOT NULL,
    	taxa	REAL DEFAULT 0,
    	payload_lenght	INTEGER NOT NULL,
    	payload	TEXT NOT NULL,
        source_address	TEXT NOT NULL,
	    destination_address	TEXT NOT NULL,
	    status	INTEGER NOT NULL,
    	PRIMARY KEY(hash_transaction)
        )""")


    db.commit()
    db.close()


dbConnect()

def insertnewtx(transaction):
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute('INSERT INTO transactions_cache (hash_transaction,taxa,payload_lenght,payload,source_address,destination_address,status) VALUES (?,?,?,?,?,?,?)',
    (transaction.id_hash, transaction.tax, transaction.payloadsize, transaction.payload, transaction.source, transaction.destination, 0))
    db.commit()
    db.close()

def readtx(idhash):
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions_cache WHERE hash_transaction = '%s'" % idhash)
    tx=cursor.fetchall()
    db.close()
    return tx

def selecttx(taxmin):
    a=[]
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions_cache WHERE taxa > %s and status =%d" %(taxmin,0))
    for i in cursor.fetchall():
        a.append((i))
    db.close()
    return a

#####################################
def updatelbtx(idhash):
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("""UPDATE transactions_cache
        SET status=1 
        WHERE hash_transaction = ?
        """, (idhash))
    db.commit()
    db.close()

def returnlbtx(idhash):
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("""UPDATE transactions_cache
        SET status=0 
        WHERE hash_transaction = ?
        """, (idhash))
    db.commit()
    db.close()

def updatefbtx(idhash):
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("""UPDATE transactions_cache
        SET status=2 
        WHERE hash_transaction = ?
        """, (idhash))
    db.commit()
    db.close()

##############################
def updatestatus(idhash,status):
    if (status <= 2 | status >= 0):
        db = sqlite3.connect(txdatabaseLocation)
        cursor = db.cursor()
        cursor.execute("""UPDATE transactions_cache
            SET status=? 
            WHERE hash_transaction = ?
            """, (status,idhash))
        db.commit()
        db.close()


def removefbtx():
    db = sqlite3.connect(txdatabaseLocation)
    cursor = db.cursor()
    cursor.execute("DELETE from transactions_cache WHERE status = 2")
    db.commit()
    db.close()
    return a

def createtx(id,lbd,avrsize,sizedesvpad):
    txtime = float(time.mktime(datetime.datetime.now().timetuple()))
    p = str(txtime)+str(id)
    idhash = hashlib.sha256(p).hexdigest()
    payloadsize = int(random.normalvariate(avrsize,sizedesvpad))
    lbd = 1/avrfee
    tax = int(random.expovariate(lbd))
    f = open('file.txt','a')
    f.truncate(payloadsize)
    f.close()
    f = open('file.txt','r')
    payload = f.read()
    tx = Transaction(idhash, payload, payloadsize, tax)
    return tx



tx= createtx(1,avrfee,avrsize,sizedesvpad)
insertnewtx(tx)

# a = 'b4aa1633ee96dd5a8c5b4a0673be95e485640e636cecadd3ec0dd273d1628ab3'

# updatestatus(a,0)
# print(readtx(a))
# print(removefbtx())





