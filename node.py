#!/usr/bin/env python

import zmq
import threading
import time
import argparse
from configparser import SafeConfigParser
import block
import blockchain
import leafchain
from leaf import Leaf
import consensus
import sqldb
import pickle
from collections import deque, Mapping, defaultdict
import logging
import rpc.messages as rpc
import hashlib
import datetime
import math
import validations
from utils import exponential_latency
import calculation
import parameter
import os
import uni_test
import socket

#TODO blockchain class and database decision (move to only db solution?)
#TODO peer management and limit (use a p2p library - pyre, kademlia?)
#TODO serialization/deserialization functions, change pickle to json?
#TODO add SQL query BETWEEN in rpcServer
#TODO check python 3+ compatibility

class StopException(Exception):
    pass

class Node(object): 
    """ Main class """

    ctx = None

    def __init__(self, ipaddr='127.0.0.1', port=9000):
        self.ipaddr = ipaddr
        self.port = int(port)
        self.balance = 1
        self.stake = 0
        self.synced = True
        self.peers = deque()
        self.bchain = None
        self.leafchains = None

        self.countRound = 0 
        self.lastRound = 0

        # ZMQ attributes
        self.ctx = zmq.Context.instance()
        self.poller = zmq.Poller()
        self.reqsocket = self.ctx.socket(zmq.REQ)
        self.repsocket = self.ctx.socket(zmq.REP)
        self.router = self.ctx.socket(zmq.REQ)
        self.rpcsocket = self.ctx.socket(zmq.REP)

        self.sendreqsocket = self.ctx.socket(zmq.REQ)
        self.repsendsocket = self.ctx.socket(zmq.REP)

        self.psocket = self.ctx.socket(zmq.PUB)
        self.subsocket = self.ctx.socket(zmq.SUB)
        self.subsocket.setsockopt(zmq.SUBSCRIBE, b'')
        self.poller.register(self.reqsocket, zmq.POLLIN)
        self.poller.register(self.router, zmq.POLLIN)
        self.poller.register(self.sendreqsocket, zmq.POLLIN)

        self.reqsocket.setsockopt(zmq.REQ_RELAXED, 1)
        
        # Flags and thread events
        self.k = threading.Event()
        self.e = threading.Event()
        self.f = threading.Event()
        self.start = threading.Event()
        self.t = threading.Event()
        self.t.clear()

        #semaphore
        self.semaphore = threading.Semaphore()
        #flag sync
        self.threadSync = threading.Event()
        self.threadSync.clear()

        #self.startSync = threading.Event()
        #self.sendBlockThread = threading.Event()
        #self.sendBlockThread.is_set()

        #miner thread
        self.miner_thread = None
        self.startMine = False

        #The last validate round

        self.lastValidateRound = 0

        #ip last block received

        self.ipLastBlock = None

        #last block received
        self.lastBlock = None

        #number of stable block
        self.stable = 0

        self.lastId = 0

        self.threads = 0

        #delays of the blocks transmition. each node has its own delay.
        #the delay uses a poison distribution with mean 8 seconds
        self.msg_arrivals = {}  
        self.inserted = {}
        self.delay = exponential_latency(parameter.AVG_LATENCY)

    # Node as client
    def connect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.connect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.connect("tcp://%s:%s" % (d_ip, d_port+1))

    def disconnect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.disconnect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.disconnect("tcp://%s:%s" % (d_ip, d_port+1))

    # Node as server
    def bind(self, socket, ip=None, port=None):
        if port and ip:
            socket.bind("tcp://%s:%s" % (ip, port))
        elif port:
            socket.bind("tcp://%s:%s" % (self.ipaddr, port))
        else:
            socket.bind("tcp://%s:%s" % (self.ipaddr, self.port))

    def close(self):
        """ Terminate and close ZMQ sockets and context """
        self.psocket.close(linger=0)
        self.subsocket.close(linger=0)
        self.repsocket.close(linger=0)
        self.rpcsocket.close(linger=0)
        self.reqsocket.close(linger=0)
        self.router.close(linger=0)
        self.ctx.term()

    def getNodeIp(self):
        return self.ipaddr
    
    def getCountRound(self):
        return self.countRound

    def addPeer(self, ipaddr):
        """ Add ipaddr to peers list and connect to its sockets  """
        peer = ipaddr if isinstance(ipaddr,Mapping) else {'ipaddr': ipaddr}
        if peer not in self.peers:
            self.peers.appendleft(peer)
            self.connect(d_ip=peer['ipaddr'],d_port=self.port)
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

    def getPeers(self):
        return self.peers

    def getThread(self):
        return self.e

    def getBchain(self):
        return self.bchain

    def addBalance(self, value):
        self.balance = self.balance + value

    #def initialSyncNode(self):
    #    while True and self.startSync.is_set():
    #        msg, ip, block_recv = self.subsocket.recv_multipart()
    #        b = pickle.loads(block_recv)
    #        i = 0
    #        arrivedTime = self.leafchains.getLastArrivedTime()
    #        round = self.leafchains.getRoundMainChain()

    #        if(validations.validateExpectedLocalRound(b,round,arrivedTime)):
    #            i = i + 1
    #            self.leafchains.setLastArrivedTime(arrivedTime)
    #            self.leafchains.setRoundMain(round)

    #        arrivedTime = b.arrive_time
    #        round = b.round
    #        if (i == 3):
    #            self.startSync.clear()
    #def testListen(self):
    #    self.bind(self.repsendsocket, port=self.port+2)
    #    time.sleep(1)
    #    while True and not self.k.is_set():
    #        try:
    #            messages = self.repsendsocket.recv_multipart()
    #            block = pickle.loads(messages[0])
    #        except:
    #            break
            #print("messageHandler")
    #        print(block)

    #        if(block):
    #            reply = "200 OK"
    #        else:
    #            reply = "Failed"

    #        self.repsendsocket.send_multipart([self.ipaddr, pickle.dumps(reply, 2)])

    #function to verify if same block is stable

    def stableBlock(self):
        #expected round
        #while(True and not self.k.is_set()):
        #startTime = int(time.mktime(datetime.datetime.now().timetuple()))
        if(not self.threadSync.is_set() and not self.e.is_set()):
            self.e.set()
            round = self.Round()
            self.stable = sqldb.setStableBlocks(round)
            self.e.clear()

        #stopTime = int(time.mktime(datetime.datetime.now().timetuple()))    
        #if((stopTime - startTime) < parameter.timeout):
        #    time.sleep(parameter.timeout - (stopTime - startTime))

    def releaseCommitBlock(self):
        self.semaphore.release()

    def commitBlock(self, message=None, t=0):
        self.semaphore.acquire()
        if(t == 0):
            #nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
            if(message):
                #get parameters
                k = message[0]
                leaf_arrivedTime = message[1]
                leaf_round = message[2]
                leaf_hash = message[3]
                leaf_index = message[4]
                cons = message[5]
                node = message[6]
                stake = message[7]
                nowTime = message[8]
                print("NowTime on Commit Block")
                print(nowTime)
                print("ArriveTime")
                print(leaf_arrivedTime)
                r = int(math.floor((nowTime - int(leaf_arrivedTime)) / parameter.timeout))
                #l[0].leaf_lastTimeTried = nowTime
                round = leaf_round + r
                #round = self.Round()
                print("Expected round mine")
                print(round)
                if(self.lastRound != round):
                    self.countRound = self.countRound + 1
                    self.lastRound = round
                    print("CONT ROUND: ", self.lastRound)
                #roundMain, indexMain, prevRoundIndex, prevIndexMain = self.leafchains.getMainChain()
                #if((leaf_index == prevIndexMain and round > roundMain and prevIndexMain != 0) or
                #(leaf_index == prevIndexMain - 1 and round > prevRoundIndex and prevIndexMain != 0)
                #or (leaf_index < (prevIndexMain - 1))):
                status,roundBlock = sqldb.verifyRoundBlock(leaf_index + 1, round)
                print("status")
                print(status)
                if(not status):
                    new_hash = None
                else:
                    new_hash, tx = cons.POS(leaf_hash, round, node, stake)
                
                if(new_hash and self.synced):
                    self.e.set() #semaforo
                    self.t.set() #semaforo listen function
                    arrive_time = int(time.mktime(datetime.datetime.now().timetuple()))
                    self.lastValidateRound = round
                    new_block = block.Block(leaf_index + 1, leaf_hash, round, node, arrive_time, new_hash, tx)
                    self.psocket.send_multipart([consensus.MSG_BLOCK, self.ipaddr, pickle.dumps(new_block, 2)])
                    new_leaf = self.leafchains.addBlockLeaf(k,new_block) 
                    if(new_leaf):
                        print("new block created")
                        print("hash")
                        print(new_block.hash)
                        print("prev_hash")
                        print(new_block.prev_hash)
                        sqldb.writeChainLeaf(new_leaf,new_block)
                        sqldb.setLogBlock(new_block, 1)
                        #self.semaphore.release()
                        return True,arrive_time

            triedTime = int(time.mktime(datetime.datetime.now().timetuple()))
            #self.semaphore.release()
            return False,triedTime
        #remove chains that can not improve its blocks
        if(t == 1):
            self.ChainClean()
            #self.semaphore.release()
            return True

        #Add new fork in blockchain. It is used in sync function process
        if(t == 3):
            if(message):
                b = message[0]
                prevHead = message[1]
                lenght = self.leafchains.addBlockLeaf(-1,b,True,prevHead)
                print("Lenght on commitBLock function")
                print(lenght)
                #self.semaphore.release()
                return lenght
            else:
                return -1

        #Add new block withiout fork in blockchain. It is used in sync function process
        if(t == 4):
            if(message):
                k = message[0]
                b = message[1]
                new_leaf = self.leafchains.addBlockLeaf(k,b,True,None)
                if(new_leaf):
                    sqldb.writeChainLeaf(new_leaf,b)
                    sqldb.setLogBlock(b, 3)
                    #self.semaphore.release()
                    return True    
                else:
                    #self.semaphore.release()
                    sqldb.setLogBlock(b,4)
                    return False
            else:
                return False

        #get the amount of stable blocks higher than a limit. It is used in uni_test to stop test after x
        # stable blocks.        
        if(t == 5):
            if(message):
                quantityBlocks = sqldb.quantityofBlocks(message[0])
                return quantityBlocks
            else:
                return -1

        #Using by uni_test to calculate some parameters like: fork number, number of blocks on simulation
         
        if(t == 6):
            if(message):
                start = message[0]
                end = message[1]
                lastForks = message[2]
                numBlocks = message[3]
                lastForks, newBlocks = calculation.calcParameters(self,start,end,lastForks, numBlocks)
                return lastForks,newBlocks
            else:
                return -1,-1
        
        #Get last stable block. It is used on uni_test
        if(t == 7):
            if(message):
                lastBlockSimulation = sqldb.getLastStableBlock(message[0])
                return lastBlockSimulation
            else:
                return - 1
        
        #Verify the round and status of pair blocks of the block that it is insering
        if(t == 8):
            if(message):
                leaf_index = message[0]
                round = message[1]
                status, blockRound = sqldb.verifyRoundBlock(leaf_index, round)
                return status, blockRound
            else:
                return False, -1
        
        #Update the stable Blocks on Local Blockchain
        if(t == 9):
            self.stableBlock()
            return True
        
        #Call HandleMessages on Consensus Function. It is used by Handler function when same node 
        #ask anything like blocks on the sync process
        if(t == 10):
            reply = consensus.handleMessages(self.bchain, message)
            return reply

        #Verify if the previows block is known 
        if(t == 11):
            if(message):
                prev_hash = message[0]
                know = sqldb.dbKnowBlock(prev_hash)
                return know
            else:
                return False
        
        #Request blocks that node does not have in the sync function
        if(t == 12):
            if(message):
                prev_hash = message[0]
                ipLastBlock = message[1]
                newBlocks = self.reqBlock(prev_hash, ipLastBlock)
                return newBlocks
            else:
                return None

        if(t == 2):
            if(message):
                k = message[0]
                b = message[1]
                new_leaf = self.leafchains.addBlockLeaf(k,b)
                if(new_leaf):
                    sqldb.writeChainLeaf(new_leaf,b)
                    sqldb.setLogBlock(b, 1)
                    return True
                else:
                    sqldb.setLogBlock(b,0)
                    return False
            else:
                return False
        return False
        

    def listen(self):
        self.bind(self.psocket)

        #come back if we neeed to simulate with latency

        #self.bind(self.repsendsocket, port=self.port+2)
        #time.sleep(1)
        while True and not self.k.is_set():
            #messages = self.repsendsocket.recv_multipart()
            #print("messageHandler")
            #print(messages[0])
            try:
                    msg, ip, block_recv = self.subsocket.recv_multipart()

                    if(ip != self.ipaddr):
    ##                self.f.clear()
    ##                newChain = False 
                    # serialize
                        b = pickle.loads(block_recv)
    ##                  logging.info("Got block %s miner %s" % (b.hash, ip))
                        b.arrive_time = int(time.mktime(datetime.datetime.now().timetuple()))
                        if(self.msg_arrivals):
                            pos = int(max(self.msg_arrivals)+1)
                            self.msg_arrivals[pos] = []
                            self.msg_arrivals[pos].append(b)
                            self.msg_arrivals[pos].append(ip)
                        else:
                            self.msg_arrivals[0] = []
                            self.msg_arrivals[0].append(b)
                            self.msg_arrivals[0].append(ip)

    ##                self.f.set()

            except (zmq.ContextTerminated):
                    print("problem on the zmq.Context")
            time.sleep(1)
    def listenInsert(self):
        """ Listen to block messages in a REQ/REP socket - We need to change from SUP to REQ/REP, because 
            the new version of the protocol has a variable delay and the blocks will be send on
            diferent times.
            Message frames: [ 'block', ip, block data ]
        """
        while True and not self.k.is_set():
                       
            if (self.msg_arrivals):
                
                self.f.clear()
                #if (not self.e.is_set()):
                #    self.e.set()
                for i, msg in list(self.msg_arrivals.iteritems()):
                    if(self.synced):
                        b = msg[0]
                        ip = msg[1]      
                        if(not self.inserted):
                            self.inserted[0] = []
                            self.inserted[0].append(i)
                        else:
                            pos = int(max(self.inserted) + 1)
                            self.inserted[pos] = []
                            self.inserted[pos].append(i)
                        # Verify block
                        #newChain = False 
                        # serialize
                        #b = pickle.loads(block_recv)
                        #logging.info("Got block %s miner %s" % (b.hash, ip))
                        #b.arrive_time = int(time.mktime(datetime.datetime.now().timetuple()))  
                        if validations.validateBlockHeader(b):
                            logging.debug('valid block header')
                            findPlace = False
                            print("NEW BLOCK ARRIVED")
                            print(b.index)
                            print(b.hash)
                            print(b.prev_hash)
                            leafs = self.leafchains.getLeafs()
                            #print(leafs)
                            for k,l in list(leafs.iteritems()):
                                if(b.prev_hash == l[0].leaf_hash):
                                    if(b.index - l[0].leaf_index == 1):
                                        if(validations.validateExpectedLocalRound(b,l[0].leaf_round, l[0].leaf_arrivedTime)
                                        and validations.validateChallenge(b,self.stake) and b.round >= l[0].leaf_round):
                                            #if(self.synced):
                                            self.commitBlock(message = [k,b],t = 2)
                                            self.semaphore.release()
                                                #new_leaf = self.leafchains.addBlockLeaf(k,b)
                                                #if(new_leaf):
                                                #    sqldb.writeChainLeaf(new_leaf,b)
                                                    #if(b.round > self.lastValidateRound):
                                                    #    self.lastValidateRound = b.round
                                                #    sqldb.setLogBlock(b,1)
                                                #else:
                                                #    sqldb.setLogBlock(b,0)
                                        else:
                                            print("Block with invalid round or the challenge was not reached")
                                            sqldb.setLogBlock(b, 0)
                                        findPlace = True    
                                        break    
                                #possible new fork on the last block
                                if(b.prev_hash == l[0].leaf_prev_hash):
                                    if(b.index - l[0].leaf_index == 0):
                                        #print(b.index)
                                        #print(leaf.prev_round)
                                        if(validations.validateExpectedLocalRound(b,l[0].leaf_prev_round,l[0].leaf_prev_arrivedTime)
                                        and validations.validateChallenge(b,self.stake)):
                                            #if(self.synced):
                                            self.commitBlock(message = [k,b],t = 2)
                                            self.semaphore.release()
                                                #print("FORK")
                                                #new_leaf = self.leafchains.addBlockLeaf(k,b)
                                                #if(new_leaf):
                                                #    sqldb.writeChainLeaf(new_leaf,b)
                                                    #if(b.round > self.lastValidateRound):
                                                    #    self.lastValidateRound = b.round
                                                #    sqldb.setLogBlock(b, 1)
                                                
                                        else:
                                            print("Block with invalid round or the challenge was not reached.")
                                            sqldb.setLogBlock(b, 0)
                                        findPlace = True    
                                        break    
                                    #possible new fork on the last last block            
                                if(b.prev_hash == l[0].leaf_prev2_hash):
                                    if(b.index - l[0].leaf_index == -1):
                                        #print("INDICES IGUAIS NO SEGUNDO BLOCO")
                                        #print(b.index)
                                        if(validations.validateExpectedLocalRound(b,l[0].leaf_prev2_round,l[0].leaf_prev2_arrivedTime)
                                        and validations.validateChallenge(b,self.stake)):
                                            #if(self.synced):
                                            print("FORK SEGUNDO BLOCO")
                                            self.commitBlock(message = [k,b], t = 2)
                                            self.semaphore.release()
                                                #new_leaf = self.leafchains.addBlockLeaf(k,b)
                                                #if(new_leaf):
                                                #    sqldb.writeChainLeaf(new_leaf,b)
                                                    #if(b.round > self.lastValidateRound):
                                                    #    self.lastValidateRound = b.round                                                  
                                                #    sqldb.setLogBlock(b, 1)
                                                                        
                                        else:
                                            print("Block with invalid round or the challenge was not reached.")
                                            sqldb.setLogBlock(b, 0)
                                        findPlace = True    
                                        break
                            self.leafchains.releaseSemaphore()
                            if(not findPlace and not self.threadSync.is_set()):
                                #sqldb.setLogBlock(b, 3)
                                self.synced = False
                                self.ipLastBlock = ip
                                print("not sync")
                                print(b.index)
                                self.lastBlock = b
                                self.threadSync.set()
                self.f.set()
                self.e.clear()            
                for msg in self.inserted:
                    del self.msg_arrivals[self.inserted[msg][0]]
                self.inserted = {}
                
                #for i, msg in list(self.msg_arrivals.iteritems()):
                #    print("blocks arrived")
                #    b = msg[0]
                #    print(b.hash)
            time.sleep(0.1)    
            #except (zmq.ContextTerminated):
            #    break
    def Round(self):
        nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
        r = int(math.floor((nowTime - int(self.leafchains.getLastArrivedTime())) / parameter.timeout)) 
        #if(r == 0 and (nowTime - int(self.leafchains.getLastArrivedTime()) < parameter.timeout)):
        #    r = 1
        round = int(self.leafchains.getRoundMainChain()) + r 
        return round
        
    def ChainClean(self):
        ##while(True and not self.k.is_set()):
            
            #startTime = int(time.mktime(datetime.datetime.now().timetuple())) 
            if(not self.threadSync.is_set()):
                ##lock = True
                ##while(lock):
                ##    if(not self.e.is_set()):
                ##        self.e.set()
                ##        lock = False

                leafs = self.leafchains.getLeafs()
                for k,l in list(leafs.iteritems()):
                    nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
                    r = int(math.floor((nowTime - int(l[0].leaf_arrivedTime)) / parameter.timeout))
                    #if(r == 0 and ((nowTime - int(l[0].leaf_arrivedTime)) < parameter.timeout)):
                    #    r = 1
                    #elif((nowTime - int(l[0].leaf_arrivedTime)) > (r * parameter.timeout)):
                    #    r = r + 1    

                    round = l[0].leaf_round + r
                    #status, blockRound = sqldb.verifyRoundBlock((l[0].leaf_index + 1), round)
                    #if(not status):
                    #    print("removeChain")
                    #    print(l[0].leaf_head)
                    #    self.leafchains.removeLeaf(k)
                    
                    #round = self.Round()
                    roundMain, indexMain, prevRoundIndex, prevIndexMain = self.leafchains.getMainChain()
                    #print("Before tests")
                    #print("INDEX LEAF")
                    #print(leaf.leaf_index)
                    #print("HEAD LEAF")
                    #print(leaf.leaf_head)
                    #print("LEAF CHAIN")
                    #print(l[0].leaf_index)
            
                    if((indexMain - l[0].leaf_index) == 1 and round > roundMain + parameter.roundTolerancy):
                        print("Remove Fork")
                        #print(l[0].leaf_head)
                        self.leafchains.removeLeaf(k)
                    elif((indexMain - l[0].leaf_index) == 2 and round > prevRoundIndex + parameter.roundTolerancy):
                        print("Remove Fork")
                        #print(l[0].leaf_head)
                        self.leafchains.removeLeaf(k)
                    elif((indexMain - l[0].leaf_index) == 3 and round > roundMain): 
                        print("Remove Fork")
                        print(l[0].leaf_head)
                        print("head")
                        print(l[0].leaf_head)
                        print("VALOR INDICE K")
                        print(k)
                        self.leafchains.removeLeaf(k)
                    elif((indexMain - l[0].leaf_index) >= 3): 
                        print("Remove Fork")
                        print(l[0].leaf_head)
                        print("head")
                        print(l[0].leaf_head)
                        print("VALOR INDICE K")
                        print(k)
                        self.leafchains.removeLeaf(k)
                #self.e.clear()
                self.leafchains.releaseSemaphore()
            #returnTime = int(time.mktime(datetime.datetime.now().timetuple()))
            #if((returnTime - startTime) < parameter.timeout):
            #    time.sleep(parameter.timeout - (returnTime - startTime))

    def mine(self, cons):
        """ Create and send block in PUB socket based on consensus """
        name = threading.current_thread().getName()

        while True and not self.k.is_set():
            # move e flag inside generate?
            self.start.wait()
            self.f.wait()

            if(self.synced):
                commited = self.commitBlock(t=1)
                self.semaphore.release()

                self.commitBlock(t=9)
                self.semaphore.release()
                
                #startNewRound
                startTime = int(time.mktime(datetime.datetime.now().timetuple()))
                print("Call's time of the Generate Block Function")
                print(startTime)

                node = hashlib.sha256(self.ipaddr).hexdigest()
                self.stake = self.balance
            
                returnTime = self.generateNewblock(startTime,node,self.stake,cons)

                print("sleeping")
                print(parameter.timeout - (returnTime - startTime))

                if(parameter.timeout > (returnTime - startTime)):
                    time.sleep(parameter.timeout - (returnTime - startTime))
                else:
                    time.sleep(parameter.timeout)
            else:
                time.sleep(0.1)
                        

    def generateNewblock(self, startTime, node, stake, cons):
        """ Loop for PoS in case of solve challenge, returning new Block object """
        #r = int(math.floor((int(time.mktime(datetime.datetime.now().timetuple())) - int(lastBlock.arrive_time)) / parameter.timeout))
        
        #startTime = int(time.mktime(datetime.datetime.now().timetuple()))
        trying = True
        chains = 0
        leafs = self.leafchains.getLeafs()
        findMine = False
        while (((int(time.mktime(datetime.datetime.now().timetuple()))- startTime) < parameter.timeout) and trying):
            for k,l in list(leafs.iteritems()):
                #print("fora lastTriedMine")
                #print(l[0].leaf_lastTimeTried)
                #print("fora lastprevLastTriedMine")
                #print(l[0].leaf_prevLastTimeTried)
                #print("l[0].leaf_index: ", l[0].leaf_index)
                #rint("indexMainChain: ", self.leafchains.getIndexMainChain())

                #nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
                #r = int(math.floor((nowTime - int(l[0].leaf_arrivedTime)) / parameter.timeout))
                #round = l[0].leaf_round + r

                #if((l[0].leaf_index < self.leafchains.getIndexMainChain()) and
                #round > self.leafchains.getRoundMainChain()):
                #    continue

                             
                status = False
                #print("lastId")
                #print(l[0].leaf_lastId)
                #print("l[0].index")
                #print(l[0].leaf_index)
                #print("lastTriedTime")
                #print(l[0].leaf_lastTimeTried)
                #print("prevLastTimeTried")
                #print(l[0].leaf_prevLastTimeTried)
                nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
                if(l[0].leaf_node != node and (l[0].leaf_lastId == (l[0].leaf_index - 1))):
                    #print("ENTROU MINE BLOCO ANTERIOR")
                    #print("entrou lastId")
                    #print(l[0].leaf_lastId)
                    #print("entrou l[0].leaf_index")
                    #print(l[0].leaf_index)
                    #print("entrou l[0].leaf_prevLastTimeTried")
                    #print(l[0].leaf_prevLastTimeTried)
                    if(l[0].leaf_prevLastTimeTried):
                        if((nowTime - int(l[0].leaf_prevLastTimeTried)) >= parameter.timeout):
                                r = int(math.floor((nowTime - int(l[0].leaf_prev_arrivedTime)) / parameter.timeout))
                                round = l[0].leaf_prev_round + r
                                #print("round MINE BLOCK ANTERIOR")
                                #print(round)
                                #status, blockRound = sqldb.verifyRoundBlock(l[0].leaf_index, round)
                                status, blockRound = self.commitBlock(message=[l[0].leaf_index,round],t=8)
                                self.semaphore.release()
                                if(status):
                                    print("Triying to use the commitBlock from Mine Block - prev block")
                                    print(nowTime)
                                    replyMine, triedTime = self.commitBlock(message=[k,l[0].leaf_prev_arrivedTime,l[0].leaf_prev_round,l[0].leaf_prev_hash,
                                    (l[0].leaf_index - 1),cons,node,stake,nowTime],t=0)
                                    self.semaphore.release()
                                    if(not replyMine):
                                        chains = chains + 1
                                    else:
                                        findMine = True
                                        chains = chains + 2
                                l[0].leaf_prevLastTimeTried = nowTime
                                l[0].leaf_lastId = l[0].leaf_index
                                #if(findMine):
                                #    break
                if(not status):
                    if(((nowTime - int(l[0].leaf_lastTimeTried)) >= parameter.timeout) and ((l[0].leaf_lastId == l[0].leaf_index)
                    or (l[0].leaf_lastId <= (l[0].leaf_index - 2)))):
                        #print("entrou lastTriedMine")
                        #print(l[0].leaf_lastTimeTried)
                        #print("entrou lastprevLastTriedMine")
                        #print(l[0].leaf_prevLastTimeTried)
                        #print("NowTime")
                        #print(nowTime)
                        print("Triying to use the commitBlock from Mine Block - last block")
                        print(nowTime)
                        replyMine, triedTime = self.commitBlock(message=[k,l[0].leaf_arrivedTime,l[0].leaf_round,
                        l[0].leaf_hash,l[0].leaf_index,cons,node, stake, nowTime], t=0)
                        self.semaphore.release()
                        if(not replyMine):
                            l[0].leaf_lastTimeTried = nowTime
                        else:
                            findMine = True

                        l[0].leaf_lastId = l[0].leaf_index
                        chains = chains + 1
                        #if(findMine):
                        #    break
                    
                        #if the node doesnt mine the last block of the chain, its possible that this node can
                        #mine older block
                    #else:
                    #    if(l[0].leaf_node != node and (l[0].leaf_lastId == (l[0].leaf_index - 1))):
                    #        print("ENTROU MINE BLOCO ANTERIOR")
                    #        print("entrou lastId")
                    #        print(l[0].leaf_lastId)
                    #        print("entrou l[0].leaf_index")
                    #        print(l[0].leaf_index)
                    #        print("entrou l[0].leaf_prevLastTimeTried")
                    #        print(l[0].leaf_prevLastTimeTried)
                    #        if(l[0].leaf_prevLastTimeTried):
                    #            if((nowTime - int(l[0].leaf_prevLastTimeTried)) >= parameter.timeout):
                    #                status, triedTime = self.commitBlock(k,leaf_arrivedTime=l[0].leaf_prev_arrivedTime,leaf_round=l[0].leaf_prev_round,
                    #                leaf_hash=l[0].leaf_prev_hash,leaf_index=(l[0].leaf_index - 1),cons = cons, node=node, stake=stake,
                    #                t=0)
                    #                self.semaphore.release()
                    #                if(not status):
                    #                    l[0].leaf_prevLastTimeTried = triedTime
                    #                    chains = chains + 1
                    #                else:
                    #                    chains = chains + 2
                    #            l[0].leaf_lastId = l[0].leaf_index
                                
        
                    #self.t.clear() #libera semaforo

                    #return block.Block(lastBlock.index + 1, lastBlock.hash, round, node, arrive_time, new_hash, tx)
                
                #time.sleep(parameter.timeout - (int(time.mktime(datetime.datetime.now().timetuple()) - startTime)))
            
                #startTime = int(time.mktime(datetime.datetime.now().timetuple()))
                #r = r + 1
                #else:
                #    return int(time.mktime(datetime.datetime.now().timetuple()))            
            if(len(leafs) >= chains): #or findMine):
                trying = False
            else:
                time.sleep(1)
        #self.leafchains.releaseSemaphore()
        #time.sleep(0.1)
        #print("Chain")
        #print(chains)
        #print("len(leafs)")
        #print(len(leafs))
        #print("return Time on Generate Block Function")
        #print(int(time.mktime(datetime.datetime.now().timetuple())))
        self.leafchains.releaseSemaphore()
        self.e.clear() #libera semaforo
        return int(time.mktime(datetime.datetime.now().timetuple()))

    #def sendBlock(self):
    #    while True and not self.k.is_set():
    #        if (self.msg_arrivals and self.sendBlockThread.is_set()):
                #print("peers")
                #print(self.peers)
    #            localTime = int(time.mktime(datetime.datetime.now().timetuple()))
                #print("Time Local sendBlock function")
                #print(localTime)
    #            if (localTime in self.msg_arrivals):
    #                for address, block in self.msg_arrivals[localTime]: 
    #                    print("address")
    #                    print(address)
    #                    self.sendreqsocket.connect("tcp://%s:%s" % (address, self.port+2))
                        #time.sleep(1)
    #                    self.sendreqsocket.send_multipart([consensus.MSG_BLOCK, self.ipaddr, pickle.dumps(block, 2)])
    #                    m = self._poll(self.sendreqsocket)[0]
    #                    self.sendreqsocket.disconnect("tcp://%s:%s" % (address, self.port+2))
    #                del self.msg_arrivals[localTime]
    #        self.sendBlockThread.clear()
    #        time.sleep(1)
    #        self.sendBlockThread.set()
            

    def probe(self):
        for i in self.peers:
            x = self.hello()
            if not x:
                self.removePeer(i)

    def validateRoundChainList(self,chain):
        i = 0
        for k,l in list(chain.iteritems()):
            itemChain = l[0]
            if(i == 0):
                if(itemChain[1] < self.lastValidateRound - parameter.roundTolerancy):
                    return False
                else:
                    lastblockRound = itemChain[1]
            else:
                blockRound = itemChain[1]
                if(blockRound <= lastblockRound):
                    return False
                lastblockRound = blockRound
            i = i + 1
        return True
    
    def validateRoundChain(self,chain):
        i = 0
        for itemChain in chain:
           
            if(i == 0):
                if(itemChain[1] < self.lastValidateRound - parameter.roundTolerancy):
                    return False
                else:
                    lastblockRound = itemChain[1]
            else:
                blockRound = itemChain[1]
                if(blockRound <= lastblockRound):
                    return False
                lastblockRound = blockRound
            i = i + 1
        return True

    def sync(self):
        while True and not self.k.is_set():
            self.threadSync.wait()
            #print("DESYNC")
            #get rBlock of all LocalChains
            #verificar de qual rBlock pertence o bloco. 
            if(self.threadSync.is_set()):

                knowBlocks = defaultdict(list)
                
                print("sync Function Called")
                i = 0
                knowBlocks[i].append(self.lastBlock)
                block = self.lastBlock

                #know = self.commitBlock(message=[block.prev_hash], t=11)
                know = sqldb.dbKnowBlock(block.prev_hash)
                #self.semaphore.release()
                while(block and (not know)):
                    print("Blocos faltantes")
                    print(block.index)
                    block = self.reqBlock(block.prev_hash, self.ipLastBlock)
                    #block = self.commitBlock(message=[block.prev_hash, self.ipLastBlock], t=12)
                    #self.semaphore.release()

                    if(not block):
                        break
                    block = pickle.loads(block)
                    block = sqldb.dbtoBlock(block)
                    i = i + 1
                    knowBlocks[i].append(block)
                    know = sqldb.dbKnowBlock(block.prev_hash)
                    #know = self.commitBlock(message=[block.prev_hash], t=11)
                    #self.semaphore.release()
                   
                #leafs = self.leafchains.getLeafs()
                #i = 0
                if(block):
                    maxId = max(knowBlocks)
                    b = knowBlocks[maxId][0]
                    #status,round = sqldb.verifyRoundBlock(b.index,b.round)
                    status, round = self.commitBlock(message=[b.index, b.round],t=8)
                    self.semaphore.release()
                    if(status):
                        print("INSERTING NEW CHAIN")
                        leafs = self.leafchains.getLeafs()
                        print("Get semaphore on sync function")
                        foundLeaf = False
                        for k,l in list(leafs.iteritems()):
                            if(l[0].leaf_hash == b.prev_hash):
                                self.leafchains.releaseSemaphore()
                                self.insertChain(k,knowBlocks)
                                foundLeaf = True
                                break
                            
                        if(not foundLeaf):
                            prevHead = sqldb.getHead(b.prev_hash)
                            print("prevHead")
                            print(prevHead)
                            index = self.commitBlock(message=[b, prevHead], t = 3)
                            print(index)
                            self.semaphore.release()
                            print("new fork on the sync function")
                            del knowBlocks[maxId]
                            self.leafchains.releaseSemaphore()
                            self.insertChain(index,knowBlocks)

                self.synced = True
                self.threadSync.clear()

    def insertChain(self,k,chain):
        leafs = self.leafchains.getLeafs()
        if(chain):
            i = len(chain) - 1
            while(i >= 0):
                b = chain[i][0]
                new_leaf = self.commitBlock(message=[k,b],t = 4)
                self.semaphore.release()
                if(not new_leaf):
                    self.leafchains.releaseSemaphore()
                    return False
                i = i - 1
            self.leafchains.releaseSemaphore()
            return True

        self.leafchains.releaseSemaphore()
        return False
  
    def recursiveValidate(self, blockerror, address=None):
        index = blockerror.index - 1
        pblock = sqldb.dbtoBlock(sqldb.blockQuery(['',index])) # previous block
        trials = 3
        while index and trials:
            logging.debug('validating index %s' % index)
            chainnew = self.reqBlocks(index + 1, index + 1, address)
            new = chainnew[0]
            new = sqldb.dbtoBlock(new)
            print ('NEW ID ON RECURSIVE', new.index)
            print ('NEW ON RECURSIVE', new.hash)
            #print("NEW", new.index)
            if new and validations.validateBlockHeader(new):
                sqldb.writeBlock(new)
                if validations.validateBlock(new, pblock) and validations.validateChallenge(new, self.stake):
                    logging.debug('returning')
                    #print('FORK', new.index)
                    return new
                else:
                    index -= 1
                    pblock = sqldb.dbtoBlock(sqldb.blockQuery(['',index]))
                    #print("PBLOCK", pblock.index)
            else:
                trials -= 1
        return new
    '''def messageHandler2(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ipaddr,self.port+3))
        while True and not self.k.is_set():
            server.listen(1)
            clientsock, clientAddress = server.accept()
            newThread = clientThread.ClientThread(clientAddress,clientsock,self.bchain)
            newThread.start()'''

    def messageHandler(self):
        """ Consensus messages in REQ/REP pattern
            Messages frames: REQ [ type, opt ]
                             REP [ ip, data ] 
        """
        self.bind(self.repsocket, port=self.port+1)
        time.sleep(1)
        while True and not self.k.is_set():
            try:
                messages = self.repsocket.recv_multipart()
            except Exception as e:
                print(str(e))
                break
            
            print("messageHandler")
            print(messages[0])
            #reply = self.commitBlock(message=messages,t=10)
            reply = consensus.handleMessages(self.bchain, messages)
            #self.semaphore.release()
            self.repsocket.send_multipart([self.ipaddr, pickle.dumps(reply, 2)])

    def rpcServer(self, ip='127.0.0.1', port=9999):
        """ RPC-like server to interact with rpcclient.py """
        self.bind(self.rpcsocket, ip, port)
        time.sleep(1)
        while True:
            try:
                messages = self.rpcsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            time.sleep(1)
            cmd = messages[0].lower()
            if cmd == rpc.MSG_LASTBLOCK:
                b = self.bchain.getLastBlock()
                self.rpcsocket.send(b.blockInfo())
            elif cmd == rpc.MSG_BLOCKCHAIN:
                b = self.bchain.Info()
                self.rpcsocket.send(b)
            elif cmd == rpc.MSG_BLOCK:
                b = sqldb.dbtoBlock(sqldb.blockQuery(messages))
                self.rpcsocket.send(b.blockInfo() if b else 'error')
            elif cmd == rpc.MSG_BLOCKS:
                l = sqldb.blocksListQuery(messages)
                blocks = []
                for b in l:
                    blocks.append(sqldb.dbtoBlock(b).blockInfo())
                self.rpcsocket.send_pyobj(blocks)
            elif cmd == rpc.MSG_ADD:
                m = self.addPeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == rpc.MSG_REMOVE:
                m = self.removePeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == rpc.MSG_PEERS:
                self.rpcsocket.send_pyobj(self.getPeers())
            elif cmd == rpc.MSG_START:
                self.rpcsocket.send_string('Starting mining...')
                if(not self.startMine):
                    self.startMine = True
                    self.miner_thread.start()
                self.start.set()
                self.f.set()
                self.e.clear()
            elif cmd == rpc.MSG_STOP:
                lock = True
                while(lock):
                    if(not self.e.is_set()):
                        self.start.clear()
                        self.f.clear()
                        self.e.set()
                        self.rpcsocket.send_string('Stopping mining...')
                        lock = False
                        self.e.clear()

            elif cmd == rpc.MSG_EXIT:
                self.rpcsocket.send_string('Exiting...')
                raise StopException
            elif cmd == rpc.MSG_BALANCE:
                self.addBalance(int(messages[1]))
                self.rpcsocket.send_string('Node Balance is ' + str(self.balance))    
            elif cmd == rpc.MSG_ADDBLOCK:
                l = []
                for i in messages[1:]: 
                    l.append(i)
                last_hash = sqldb.dbtoBlock(sqldb.blockQuery(['',str(int(l[0])-1)])).hash
                hash_node = hashlib.sha256(self.ipaddr).hexdigest()
                time_create = int(time.mktime(datetime.datetime.now().timetuple()))
                c_header = str(last_hash) + str(l[1]) + str(hash_node)
                hash = hashlib.sha256(c_header).hexdigest()
                b = block.Block(int(l[0]), last_hash, int(l[1]), hash_node,time_create, hash)
                sqldb.writeBlock(b)
                #sqldb.writeChain(b)
                self.bchain.addBlocktoBlockchain(b)
                self.rpcsocket.send_string('Block created ' + str(b.blockInfo()))
                
                self.psocket.send_multipart([consensus.MSG_BLOCK, self.ipaddr, pickle.dumps(b, 2)])
            else:
                self.rpcsocket.send_string('Command unknown')
                logging.warning('Command unknown')

# Client request-reply functions

    def _poll(self, socket=None):
        # Poll socket for 5s checking if any arriving reply messages
        s = socket if socket else self.reqsocket
        try:
            evts = dict(self.poller.poll(5000))
        except KeyboardInterrupt:
            return None, None
        if s in evts and evts[s] == zmq.POLLIN:
            m = s.recv_multipart()
            return pickle.loads(m[-1]), m[-2]
        else:
            logging.debug('No response from node (empty pollin evt)')
            return None, None

    def reqLastBlock(self):
        """ Messages frames: [ 'getlastblock', ] """
        self.reqsocket.send_multipart([consensus.MSG_LASTBLOCK,])
        logging.debug('Requesting most recent block')
        m, address = self._poll()
        return sqldb.dbtoBlock(m), address

    #def reqBlock(self, index):
    #    """ Messages frames: [ 'getblock', index ] """
    #    self.reqsocket.send_multipart([consensus.MSG_BLOCK, str(index)])
    #    logging.debug('Requesting block index %s' % index)
    #    m = self._poll()[0]
    #    print("BLOCO REQBLOCK",m )
    #    return sqldb.dbtoBlock(m)

    def reqBlocks(self, first, last, address=None):
        """ Messages frames: [ 'getblocks', from index, to index ] """
        if address:
            # using another socket for direct ip connect, avoiding round-robin
            self.router.connect("tcp://%s:%s" % (address, self.port+1))
            time.sleep(1)
            logging.debug('Requesting blocks %s to %s', first, last)
            self.router.send_multipart([consensus.MSG_BLOCKS, str(first), str(last)])
            m = self._poll(self.router)[0]
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            self.reqsocket.send_multipart([consensus.MSG_BLOCKS, str(first), str(last)])
            logging.debug('Requesting blocks %s to %s', first, last)
            m = self._poll()[0]
        return m

    def reqLeaves(self, address=None):
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            time.sleep(1)
            self.router.send_multipart([consensus.MSG_LEAVES])
            m = self._poll(self.router)[0]
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            print(consensus.MSG_LEAVES)
            self.reqsocket.send_multipart([consensus.MSG_LEAVES])
            #logging.debug('Requesting blocks %s to %s', first, last)
            m = self._poll()[0]
        return m

    '''def reqBlock(self,blockHash, address = None):
        m = None
        HEADERSIZE = 10
        if address:
            print("syncing with NODE:", address)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                msglen = 0
                client.connect((address, self.port+3))
                print([consensus.MSG_REQBLOCK,str(blockHash)])
                msg = pickle.dumps([consensus.MSG_REQBLOCK,str(blockHash)],2)
                
                lenmsg = str(len(msg))
                header = ''
                header = header.ljust(HEADERSIZE - len(lenmsg))
                lenmsg = str(lenmsg) + header
                lenmsg = bytes(lenmsg)
                msg=lenmsg+msg
                client.send(msg)
                
                #get new block
                full_msg = ''
                msg = client.recv(16)
                msglen = int(msg[:HEADERSIZE])
                print(msglen)
                full_msg+=msg
                while(len(full_msg)-HEADERSIZE < msglen):
                    msg = client.recv(16)
                    full_msg+=msg

                m = pickle.loads(full_msg[HEADERSIZE:])
                print(m)
            except Exception as e:
                print(str(e))
            #print m
            client.close()
        return m'''

    def reqBlock(self, blockHash, address = None):
        m = None
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            print("IP")
            print(address)

            time.sleep(1)
            try:
                self.router.send_multipart([consensus.MSG_REQBLOCK,str(blockHash)])
                m = self._poll(self.router)[0]
            except Exception as e:
                print(str(e))
                
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            try:
                self.reqsocket.send_multipart([consensus.MSG_REQBLOCK,str(blockHash)])
                #logging.debug('Requesting blocks %s to %s', first, last)
                m = self._poll()[0]
            except Exception as e:
                print(str(e))
        return m

    def reqBlocksChain(self, localHash, remoteTargetHash, address=None, ):
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            print("IP")
            print(address)

            time.sleep(1)
            self.router.send_multipart([consensus.MSG_BLOCKCHAIN,str(localHash),str(remoteTargetHash)])
            m = self._poll(self.router)[0]
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            self.reqsocket.send_multipart([consensus.MSG_BLOCKCHAIN,str(localHash),str(remoteTargetHash)])
            #logging.debug('Requesting blocks %s to %s', first, last)
            m = self._poll()[0]
        return m

    def reqAllChain(self, head, address=None):
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            time.sleep(1)
            self.router.send_multipart([consensus.MSG_ALLCHAIN,str(head)])
            m = self._poll(self.router)[0]
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            self.reqsocket.send_multipart([consensus.MSG_ALLCHAIN,str(head)])
            #logging.debug('Requesting blocks %s to %s', first, last)
            m = self._poll()[0]
        return m

    def reqSendHeadsChains(self,forkHash, headChains, blockHash,  address=None):
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            time.sleep(1)
            self.router.send_multipart([consensus.MSG_REQBLOCKS,str(forkHash),pickle.dumps(headChains),str(blockHash)])
            m = self._poll(self.router)[0]
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            self.reqsocket.send_multipart([consensus.MSG_REQBLOCKS,str(forkHash),pickle.dumps(headChains),str(blockHash)])
            #logging.debug('Requesting blocks %s to %s', first, last)
            m = self._poll()[0]
        return m
 
    def hello(self):
        """ Messages frames: [ 'hello', ] """
        self.reqsocket.send_multipart([consensus.MSG_HELLO,])
        logging.debug('Probing peer alive')
        m = self._poll()[0]
        return m

# Main program

_LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

def _log_level_to_int(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise argparse.ArgumentTypeError('Invalid log level: %s' % loglevel)
    return numeric_level

def main():
    # Argument and command-line options parsing
    parser = argparse.ArgumentParser(description='Blockchain simulation')
    parser.add_argument('-i', '--ip', metavar='ip', dest='ipaddr',
                        help='Specify listen IP address', default='127.0.0.1')
    parser.add_argument('-p', '--port', metavar='port', dest='port',
                        help='Specify listen port', default=9000)
    parser.add_argument('--peers', dest='peers', nargs='*',
                        help='Specify peers IP addresses', default=[])
    parser.add_argument('--miner', dest='miner', action='store_true',
                        help='Start the node immediately mining')
    parser.add_argument('--log', dest='loglevel', type=_log_level_to_int, nargs='?', default='warning',
                        help='Set the logging output level {0}'.format(_LOG_LEVEL_STRINGS))
    parser.add_argument ('-c', '--config', dest='config_file', default='node.conf', type=str,
                        help='Specify the configuration file')
    args = parser.parse_args()
    args.diff = 5
    # Configuration file parsing (defaults to command-line arguments if not exists)
    cfgparser = SafeConfigParser({'ip': args.ipaddr, 'port': str(args.port), 'peers': args.peers, 'miner': str(args.miner).lower(), 'loglevel': 'warning', 'diff': '5'})
    if cfgparser.read(args.config_file):
        args.peers = cfgparser.get('node','ip')
        args.port = int(cfgparser.get('node','port'))
        args.peers = cfgparser.get('node','peers').split('\n')
        args.miner = cfgparser.getboolean('node','miner')
        args.diff = int(cfgparser.get('node','diff'))
        args.loglevel = _log_level_to_int(cfgparser.get('node','loglevel'))
    # File logging
    logging.basicConfig(filename='log/example.log', filemode='w', level=_log_level_to_int('debug'),
        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S')
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(args.loglevel)
    logging.getLogger('').addHandler(console)

    
    #sqldb.databaseLocation = 'blocks/blockchain.db'
    cons = consensus.Consensus()
    
    n = Node(args.ipaddr, args.port)
    n.threads = []
    # Connect to predefined peers
    if args.peers:
        iplist = args.peers if isinstance(args.peers, list) else [args.peers]
        for ipaddr in iplist:
            n.addPeer(ipaddr)
    else: # Connect to localhost
        logging.info('Connecting to localhost...')
        n.connect()
    time.sleep(1)

    # Connect and check own node database
    logging.info('checking database')
    sqldb.dbConnect()
    n.bchain = sqldb.dbCheck()
    n.leafchains = sqldb.dbCheckLeaf(n.bchain)
    n.lastValidateRound = n.leafchains.getRoundMainChain()
    
    #msg_thread2 = threading.Thread(name='REQ/REP2', target=n.messageHandler2)
    #msg_thread2.start()
    # Thread to listen request messages
    msg_thread = threading.Thread(name='REQ/REP', target=n.messageHandler)
    msg_thread.start()
    n.threads.append(msg_thread)

    #start sync the node.
    #node_sync_thread = threading.Thread(name='PUB/SUB', target=n.initialSyncNode)
    #node_sync_thread.start()
    #threads.append(node_sync_thread)
    #n.startSync.set()

    # Thread to listen broadcast messages
    listen_thread = threading.Thread(name='PUB/SUB', target=n.listen)
    listen_thread.start()
    n.threads.append(listen_thread)

    listenInsert_thread = threading.Thread(name='listenInsert', target=n.listenInsert)
    listenInsert_thread.start()
    n.threads.append(listenInsert_thread)

    
    # Thread to Sync node
    sync_thread = threading.Thread(name='sync', target=n.sync)
    sync_thread.start()
    n.threads.append(sync_thread)

    #thread_sendBlock
    #sendBlock_thread = threading.Thread(name='sendBlock', target=n.sendBlock)
    #sendBlock_thread.start()
    #threads.append(sendBlock_thread)

    #thread to count stable blocks
    #stableBlock_thread = threading.Thread(name='stableBlock', target=n.stableBlock)
    #stableBlock_thread.start()
    #threads.append(stableBlock_thread)

    #thread ChainClean
    #chainClean_thread = threading.Thread(name='chainClean', target=n.ChainClean)
    #chainClean_thread.start()
    #threads.append(chainClean_thread)

    # Check peers most recent block
    #n.sync()

    # Miner thread
    n.miner_thread = threading.Thread(name='Miner', target=n.mine,
         kwargs={'cons': cons})
    n.threads.append(n.miner_thread)

    #print(threads)

    if args.miner:
        n.miner_thread.start()
        n.start.set()
        n.f.set()

    #start uni_test
    #uni_test.timetocreateblocks(n)
    # Main program thread
    #h.cmd('nohup python node.py -i', h.IP(), '-p 9000 --peers %s &' % peers)
    #textNode = pickle.dumps(n,2)
    #test = "OI"
    #os.system('sudo python uni_test.py -n %s' % text)

    #call timetocreateblocks function to automatic simulation
    time.sleep(1)
    uniTest_thread = threading.Thread(name='uniTest', target=uni_test.timetocreateblocks, kwargs={'node':n})
    uniTest_thread.start()

    try:
        while True:
            # rpc-like commands
            n.rpcServer()
    # Exit main and threads
    except (KeyboardInterrupt, StopException):
        pass
    finally:
        n.k.set()
        n.e.set()
        n.f.set()
        n.start.set()
        n.close()
        for t in threads:
           t.join()
        print(n.bchain.Info())

if __name__ == '__main__':
    main()
