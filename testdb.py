#!/usr/bin/env python
# import sqlite3
# import logging
# from block import Block
# import block
# from block import Block
# from felipe import Transaction
# import blockchain
# import leaf
# import parameter
# import datetime
# import time
# import hashlib
# from collections import deque, Mapping, defaultdict
# import pickle
# import math
import mysql.connector
# import chaincontrol
# from decimal import Decimal
# from random import randint
# logger = logging.getLogger(__name__)

def mydbConnect():
    db = mysql.connector.connect(user='teste', password='12345678',host='localhost',database='blockchain', auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
        id integer(100) NOT NULL,
        round integer,
        prev_hash text,
        hash VARCHAR(256) NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id, hash))""")
    

    cursor.execute("""CREATE TABLE IF NOT EXISTS chain (
        id integer(100) NOT NULL,
        round integer,
        prev_hash text,
        hash text NOT NULL,
        node text,
        mroot text,
        tx text,
        arrive_time text,
        PRIMARY KEY (id))""")
        
    cursor.execute("""CREATE TABLE IF NOT EXISTS localChains (
        idChain integer(100) NOT NULL,
        id integer(100) NOT NULL,
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
      startFork text default ('0'),
      endFork text default ('0'))""")
    
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
      id INTEGER(100) NOT NULL,
      sround INTEGER NOT NULL,
      endround INTEGER NOT NULL,      
      PRIMARY KEY (id))""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS block_reversion (
      idreversion INTEGER(100) NOT NULL,
      idrevblock INTEGER(100),
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

mydbConnect()