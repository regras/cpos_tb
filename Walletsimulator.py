#!/usr/bin/env python
import random
import sqlite3
import socket
import logging
from block import Block
import block
from block import Block
#import blockchain
import leaf
import parameter
import consensus
import datetime
import time
import hashlib
from collections import deque, Mapping, defaultdict
import pickle
import math
#import chaincontrol
from bloomfilter import BloomFilter
from decimal import Decimal
from random import randint
import threading
from thread import *
logger = logging.getLogger(__name__)



class wallet(object):
    def __init__(self, ipaddr='127.0.0.1', port=9000):
        self.ipaddr = ipaddr
        self.port = int(port)
        self.avrfee = 100.0
        self.avrsize = 600
        self.sizedesvpad = 100
        self.brec = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bloomf = BloomFilter(1000)
        self.peers = deque()

    def disconnect(self,d_ip='127.0.0.1',d_port=9000):
        self.reqsocket.disconnect("tcp://%s:%s" % (d_ip, d_port+1))

    def addPeer(self, ipaddr):
        """ Add ipaddr to peers list and connect to its sockets  """
        peer = ipaddr if isinstance(ipaddr,Mapping) else {'ipaddr': ipaddr}
        if peer not in self.peers:
            self.peers.appendleft(peer)
            return "Peer %s connected" % peer['ipaddr']
        else:
            logging.warning("Peer %s already connected" % peer['ipaddr'])
            return "Peer %s already connected" % peer['ipaddr']

    def removePeer(self, ipaddr):
        """ Remove peer with ipaddr and disconnect to its sockets  """
        peer = ipaddr if isinstance(ipaddr,Mapping) else {'ipaddr': ipaddr}
        try:
            self.peers.remove(peer)
            self.disconnect(d_ip=peer['ipaddr'],d_port=self.port)
            time.sleep(1)
        except ValueError:
            logging.warning("Peer %s not connected" % peer['ipaddr'])
            return "Peer %s not connected" % peer['ipaddr']
        return "Peer %s removed" % peer['ipaddr']


    def sendtx(self,msgtx):
        tx = msgtx[0]
        ip = msgtx[1]
        bloom_filter = msgtx[2]
        setsend=[]
        for k in self.peers:
            if(not self.bloomf.check(k['ipaddr'],bloom_filter)):    
                setsend = setsend + [k['ipaddr']]
                self.bloomf.add(k['ipaddr'],bloom_filter)
        message = [consensus.MSG_TX, ip, tx, bloom_filter]
        message = pickle.dumps(message,2)
        for k in psetsend:
            try:
                tsend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tsend.connect((k,self.port))                                      
                tsend.send(message)
                m = tsend.recv(4096)
                tsend.close()
            except Exception as e:
                print(str(e))

    def createtx(self, id, lbd, avrsize, sizedesvpad):
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
        bloom_filter = self.bloomf.new_filter()
        self.bloomf.add(self.ipaddr, bloom_filter)
        mtx = [new_tx, self.ipaddr, bloom_filter]
        start_new_thread(self.sendtx, (mtx,))