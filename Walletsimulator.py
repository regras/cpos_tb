#!/usr/bin/env python
import random
import sqlite3
import mysql.connector
import socket
import logging
from block import Block
import block
import sqldb

# import blockchain
import leaf
import parameter
import consensus
from testedb import Transaction
import datetime
import time
import hashlib
from collections import deque, Mapping, defaultdict
import pickle
import math

# import chaincontrol
from bloomfilter import BloomFilter
from decimal import Decimal
from random import randint
import threading
from thread import *

logger = logging.getLogger(__name__)


class wallet(object):
    def __init__(self, ipaddr="127.0.0.1", porttx=9010, n=2, rate=0.011):
        self.ipaddr = ipaddr
        self.n = int(n)
        self.porttx = int(porttx)
        self.rate = rate
        self.avrfee = 15.0
        self.avrsize = 600
        self.sizedesvpad = 100
        self.brec = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bloomftx = BloomFilter(1000)
        self.peers = parameter.peers

    def getpeers(self):
        selectedpeers = []
        first = 1
        for i in range(self.n):
            if first == 1:
                first = 0
                s = random.randint(0, (len(self.peers) - 1))
                selectedpeers.append(self.peers[s])
                a = [s]
            if first == 0:
                while s in a:
                    s = random.randint(0, (len(self.peers) - 1))
                selectedpeers.append(self.peers[s])
                a.append(s)
        return selectedpeers

    def sendtx(self, msgtx):
        nodes = self.getpeers()
        tx = msgtx[0]
        ip = msgtx[1]
        bloom_filter = msgtx[2]
        print("#####sending transaction:", tx.id_hash)
        print("#####Nodes:", nodes[0], "AND", nodes[1])
        setsend = []
        for k in nodes:
            if not self.bloomftx.check(k, bloom_filter):
                setsend = setsend + [k]
                self.bloomftx.add(k, bloom_filter)
        message = [consensus.MSG_TX, ip, tx, bloom_filter]
        message = pickle.dumps(message, 2)
        for k in setsend:
            try:
                tsend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tsend.connect((k, self.porttx))
                tsend.send(message)
                m = tsend.recv(4096)
                tsend.close()
            except Exception as e:
                print(str(e))

    def createtx(self, lasttime):
        ratelbd = 1 / self.rate
        t = random.expovariate(ratelbd)
        if (time.time() - lasttime) < t:
            try:
                time.sleep(float(t - (time.time() - lasttime)))
            except Exception as e:
                print(str(e))
        txtime = time.time()
        # print('truetime: %s expectedtime: %s',(txtime-lasttime,t))
        p = str("{0:5f}".format(txtime)) + str(self.ipaddr)
        idhash = hashlib.sha256(p).hexdigest()
        # print(idhash)
        payloadsize = int(random.normalvariate(self.avrsize, self.sizedesvpad))
        lbd = 1 / self.avrfee
        tax = int(random.expovariate(lbd))
        payload = b"0" * payloadsize
        new_tx = Transaction(idhash, payload, payloadsize, tax)
        bloom_filter = self.bloomftx.new_filter()
        self.bloomftx.add(self.ipaddr, bloom_filter)
        mtx = [new_tx, self.ipaddr, bloom_filter]
        start_new_thread(self.sendtx, (mtx,))
        # sqldb.insertnewtx(new_tx)
        return txtime


def main():
    w = wallet()
    # starttime = time.time()
    lasttime = time.time()
    while True:
        lasttime = w.createtx(lasttime)


main()
