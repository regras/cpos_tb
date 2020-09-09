#!/usr/bin/env python

import zmq
import threading
import time
import argparse
from configparser import SafeConfigParser
from block import Block
import blockchain
import consensus
import sqldb
import chaincontrol
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
import random
from operator import itemgetter


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
        self.localSalt = hashlib.sha256(str(random.random())).hexdigest()
        self.balance = 1
        self.resync = 0
        self.peers = deque()
        self.startround = 0
        self.connectPeers = deque()
        self.acceptPeers = {}
        #self.discoveryPeers = defaultdict(list)
        self.bchain = None
        self.node = hashlib.sha256(self.ipaddr).hexdigest()
        self.stake = 1
        self.countRound = 0 
        self.lastRound = 0
        self.cons = None
        self.firstsync = 0
        self.lround = 0
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
        #self.minecontrol = threading.Event()
        self.t = threading.Event()
        self.listen_signal = threading.Event()
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
        self.send_time = {}

        #self.msg_arrivals_out_order = {}
        #self.inserted_out_order = {}
        #index = parameter.peers.index(self.ipaddr)
        #self.delay = exponential_latency(parameter.AVG_LATENCY[index])

    def restart(self):
        self.router.setsockopt(zmq.LINGER,0)
        self.router.close()
        self.poller.unregister(self.router)

        self.router = self.ctx.socket(zmq.REQ)
        self.poller.register(self.router, zmq.POLLIN)
        


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
    
    def setFirstSync(self,firstsync):
        self.firstsync = int(firstsync)

    def setStake(self,stake):
        self.stake = int(stake)

    def getNodeIp(self):
        return self.ipaddr
    
    def setCons(self,cons):
        self.cons = cons
    
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

    #function sortition. This function return the number of sub-user raffled on round
    def getNumAccepted(self):
        return len(self.acceptPeers)

    def insertAcceptPeer(self,ip,d):
        if(ip not in self.acceptPeers):
            self.acceptPeers[ip] = d
            #print ("accepted peers: ", self.acceptPeers)
            if(self.ipaddr in parameter.trusted):
                if({'ipaddr': ip} not in self.peers):
                    self.addPeer(ip)            
            #print("peers: ", self.peers)

    def checkDistance(self,ip,d):
        if(ip not in self.acceptPeers):
            for i in self.acceptPeers:
                if(int(d) < int(self.acceptPeers[i])):
                    return True
        return False 

    def getIp(self):
        return self.ipaddr    

    def getLocalSalt(self):
        return self.localSalt
    
    def trusted(self):
        for i in parameter.trusted:
            if(i in self.connectPeers):
                return True
        return False

    '''#fverifying if antecessor end the neighboor process
    def search_string(self,string):
        fileName = 'allnodeconnected.txt'
        if(os.path.isfile(fileName)):
            results = open(fileName, 'r')
            text = results.readlines()
            for i in text:
                if string in i:
                    results.close()
                    return True
            results.close()
        return False'''


#########neighbor connect function ###############
    def neighbors(self,ipaddr=None,stakeList=None,firstC=True,pPeers=0):
        print("starting peer connecting...")
        peers = parameter.peers
        trust = parameter.trusted
        stake = parameter.numStake

        #waiting until peer imediattly before connect
        '''if(firstC):
            index = peers.index(ipaddr)
            ip = None
            if(index > 0):
                ip = peers[index - 1]
            
            while(not self.search_string(ip) and ip):
                time.sleep(1)
        
            if(ipaddr in trust):
                for i in trust:
                    if(i != ipaddr):
                        self.connectPeers.appendleft(i)'''

        time.sleep(10)
        peer = len(self.connectPeers)

        if(not firstC):
            limitP = peer + pPeers
        else:
            limitP = parameter.k
        
        if(ipaddr in trust):
            for i in trust:
                if(i != ipaddr):
                    self.connectPeers.appendleft(i)
                    peer = peer + 1

        while(peer < limitP):
            #print("peer: ", peer)
            nowTime = time.mktime(datetime.datetime.now().timetuple())
            currentRound = int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/parameter.timeout))
            #print("starting new peering round: ", currentRound)
            salt = hashlib.sha256(str(currentRound)).hexdigest()
            distances = {}                       
            for i in peers:                
                if(i != ipaddr and i not in self.connectPeers):
                    peerSalt = str(i) + str(salt)
                    distance = int(hashlib.sha256(str(ipaddr)).hexdigest(),16) ^ int(hashlib.sha256(peerSalt).hexdigest(),16)
                    distances[distance] = i

            #trying connect new peers
            #print("distance list", distances)
            for i, msg in sorted(distances.items(), key=itemgetter(0)):
                if(int(i) <= float(parameter.theta * (2**256 - 1))):
                    if(peer < parameter.k):
                        #status = False
                        if(self.trusted()):
                            status = self.peeringRequest(salt,msg)
                            if(status):
                                #print("threshold: ", float(i) / (2**256 - 1))
                                #print("status: ", status)                    
                                #print("new peer connected: ", msg)
                                self.connectPeers.appendleft(msg)
                                peer = peer + 1
                        else:
                            if(msg in trust):
                                status = self.peeringRequest(salt,msg)
                                if(status):
                                    #print("threshold: ", float(i) / (2**256 - 1))
                                    #print("status: ", status)                    
                                    #print("new peer connected: ", msg)
                                    self.connectPeers.appendleft(msg)
                                    peer = peer + 1
                            elif(peer < parameter.k - 1):
                                status = self.peeringRequest(salt,msg)
                                if(status):
                                    #print("threshold: ", float(i) / (2**256 - 1))
                                    #print("status: ", status)                    
                                    #print("new peer connected: ", msg)
                                    self.connectPeers.appendleft(msg)
                                    peer = peer + 1
                            
            if(peer >= parameter.k):
                break

            print("dif time: ", parameter.timeout - (time.mktime(datetime.datetime.now().timetuple()) - nowTime))
            if(time.mktime(datetime.datetime.now().timetuple()) - nowTime < parameter.timeout):
                print("sleeping: ", parameter.timeout - (time.mktime(datetime.datetime.now().timetuple()) - nowTime))
                time.sleep(parameter.timeout - (time.mktime(datetime.datetime.now().timetuple()) - nowTime))
            

        #print("connected peers: ", self.connectPeers)
        for i in self.connectPeers:
            if({'ipaddr': i} not in self.peers):
                self.addPeer(i)
        print("peers connected: ", self.peers)
        
        if(firstC):
            #inform others peers that connected process is over
            fileName = '/datavolume/allnodeconnected.txt'
            results = open(fileName, 'a')
            results.write(str(ipaddr) + '\n')
            results.close()

            #check if all peers was connected
            fileName = '/datavolume/allnodeconnected.txt'
            if(os.path.isfile(fileName)):
                status = False
                while(not status):
                    results = open(fileName, 'r')
                    read = results.readlines()
                    if len(read) >= parameter.nodes:
                        status = True
                    results.close()
                    time.sleep(1)

            self.startThreads(stakeList)       
                    
#######end neightbor function#######

#######start all threads after connect neighbor######
    def startThreads(self,stakeList):

        # Thread to listen broadcast messages
        listen_thread = threading.Thread(name='PUB/SUB', target=self.listen)
        listen_thread.start()
        self.threads.append(listen_thread)    


        listenInsert_thread = threading.Thread(name='listenInsert', target=self.listenInsert)
        listenInsert_thread.start()
        self.threads.append(listenInsert_thread)
        
        # Thread to Sync node
        sync_thread = threading.Thread(name='sync', target=self.syncNode)
        sync_thread.start()
        self.threads.append(sync_thread)

        #start Mine
        nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
        currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME)) / parameter.timeout))                           
        if(not self.startMine):
            self.miner_thread = threading.Thread(name='Miner', target=self.mine)
            self.threads.append(self.miner_thread)
            self.startMine = True

            self.startround = currentRound + 1
            self.miner_thread.start()
        currentRound = parameter.timeout * currentRound                
        print("Sleeping time: ", parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound))
        time.sleep(parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound))                
        self.start.set()
        self.f.set()
                
        
        #send_block_thread = threading.Thread(name='send_block',target=self.send_block)
        #send_block_thread.start()
        #self.threads.append(send_block_thread)

        #thread to count stable blocks
        #stableBlock_thread = threading.Thread(name='stableBlock', target=self.stableBlock)
        #nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
        #print("NOWTIME: ",nowTime)
        #currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME)) / parameter.timeout))                    
        #currentRound = parameter.timeout * currentRound
        #print("currentRound: ",currentRound)                
        #print("Sleeping time: ", parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound))
        #time.sleep(parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound)) 
        #stableBlock_thread.start()
        #self.threads.append(stableBlock_thread)

        #call timetocreateblocks function to automatic simulation
        #print('waiting %f seconds to sync the start' %(360 - (nowTime - float(time.mktime(datetime.datetime.now().timetuple())))))
        #time.sleep(360 - (nowTime - float(time.mktime(datetime.datetime.now().timetuple()))))
        #uniTest_thread = threading.Thread(name='uniTest', target=uni_test.timetocreateblocks, kwargs={'node':self,'stake':stakeList})
        #uniTest_thread.start()

#######end threads connecting ############ 


    def stableBlock(self):
        #prevTime = float(parameter.GEN_ARRIVE_TIME)
        #prevRound = 0
        #self.lround = 0
        if(self.firstsync == 1):
            nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
            currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))    
            self.lastRound = currentRound
            self.resync = 0
            self.threadSync.set()

        #while True and not self.k.is_set():            
        if(not self.threadSync.is_set()):
            nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
            #print("nowTime: ", nowTime)
            #if((nowTime - prevTime) >= parameter.timeout): 
            #    prevTime = nowTime
            currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))
            #check if buffer has same block to insert before check new committed blocks
            #self.listen_signal.set() 
            #time.sleep(0.1) #wait a few time to guaranteed that listen thread get the semaphore first

            self.semaphore.acquire()                                       
            print("STABLE ROUND: ", currentRound)
            self.lround,sync = sqldb.reversionBlock(currentRound,self.lround)
            if(not sync):
                self.lastRound = currentRound
                self.resync = 0
                self.threadSync.set()
                #self.minecontrol.clear()
            self.semaphore.release()
            #else:
            #print("SLEEP TIME: ", (parameter.timeout - (float(time.mktime(datetime.datetime.now().timetuple())) - nowTime)))
            #if(float(time.mktime(datetime.datetime.now().timetuple())) - nowTime < parameter.timeout):
            #    time.sleep(parameter.timeout - (float(time.mktime(datetime.datetime.now().timetuple())) - nowTime))
            #else:
            #    time.sleep(1)

    def acquireCommitBlock(self):
        self.semaphore.acquire()
        
    def releaseCommitBlock(self):
        self.semaphore.release()

    def commitBlock(self, message=None, t=0):
        #self.semaphore.acquire()
        if(t == 0):
            #nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
            if(message):
                #get parameters
                block = message[0]
                #cons = message[1]                
                round = message[1]
                #nowTime = time.mktime(datetime.datetime.now().timetuple())
                #round = int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/parameter.timeout))
                status,roundBlock = sqldb.verifyRoundBlock(block.index + 1, round)
                print("STATUS ROUND: ", status)
                if(not status or round <= block.round):
                    proofHash = None
                else:
                    tx = chr(random.randint(1,100)) #we need create same block payload in the future
                    userHash, blockHash = self.cons.POS(lastBlock_hash=block.hash,round=round,node=self.node,tx=tx)
                    subUser = validations.sortition(userHash,self.stake,self.cons)
                    if(subUser > 0):
                        proofHash, prioritySubUser = self.cons.calcProofHash(userHash,blockHash,subUser)
                    else:
                        print("USER NOT RAFLED")
                        proofHash = None
                
                if(proofHash):
                    self.e.set() #semaforo
                    self.t.set() #semaforo listen function
                    arrive_time = int(time.mktime(datetime.datetime.now().timetuple()))

                    #block hash is BlockHash + proofHash
                    block_header = str(blockHash) + str(proofHash)
                    blockHash = hashlib.sha256(str(block_header)).hexdigest()
                    print("HASH BLOCK: ", blockHash)
                    print("IP NODE: ", self.ipaddr)
                    new_block = Block(block.index + 1, block.hash, round, self.node, arrive_time, blockHash, tx, subUser, proofHash)
                    sqldb.setArrivedBlock(new_block,1)
                    sqldb.setLogBlock(new_block, 1)
                    status = chaincontrol.addBlockLeaf(block=new_block)
                    #print("status: ", status) 
                    if(status):  
                        #self.insertNewBlock(message=[self.ipaddr, str(self.stake), new_block])                      
                        try:
                            self.psocket.send_multipart([consensus.MSG_BLOCK, self.ipaddr, str(self.stake), pickle.dumps(new_block, 2)])                    
                        except zmq.ZMQError as e:
                            print("psocket on mine function has a problem!")
                            print(str(e))
                        #self.semaphore.release()
                        return True,arrive_time
                    #else:
                        #print("block is not priority. Not inserted")

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
                hash = message[0]
                know = sqldb.dbKnowBlock(hash)
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

        if(t == 13):
            blocks = sqldb.getAllKnowChains()
            return blocks

        if(t == 14):
            hash = message[0]
            blockPrev = sqldb.getBlock(hash)
            return blockPrev

        if(t == 2):
            if(message):
                b = message[0]
                status = chaincontrol.addBlockLeaf(block=b)                
                return status

        #verifying if log_block table has the new block
        if(t == 15):
            hash = message[0]
            status = sqldb.knowLogBlock(hash)
            return status

        if(t == 16):
            blocks = message[0]
            stake = parameter.numStake
            #print("logblock: ", logblock)
            sumsuc = 0
            if(blocks):
                for item in blocks:
                    checkProof, subUser = validations.validateProofHash(item,stake[1][item.node][0],self.cons)
                    if(checkProof):
                        sumsuc = sumsuc + subUser
                        sqldb.setLogBlock(item,1)

            #if(b):        
            #    sqldb.setLogBlock(b,1)
            #    sqldb.removeBlock(b.round)
            #    idChain = sqldb.getIdChain(b.prev_hash)
            #    sqldb.writeChainLeaf(idChain,b)
                #sqldb.reversionBlock(b.round,self.lround)
            return True, sumsuc     
        return False  

    '''def send_block(self):
        delay = int(time.mktime(datetime.datetime.now().timetuple()))
        nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
        while True and not self.k.is_set():
            #print("DELAY: ", delay)            
            if delay in self.send_time:                
                for j in self.send_time[delay]:                    
                    ip = self.send_time[delay][j][0]
                    stake = self.send_time[delay][j][1]
                    block = self.send_time[delay][j][2]
                    block.arrive_time = float(time.mktime(datetime.datetime.now().timetuple()))
                    #print("####SEND BLOCK####")
                    #print("SEND BLOCK TIME: ",int(time.mktime(datetime.datetime.now().timetuple())))
                    #print("##END SEND BLOCK##")
                    if(validations.validateExpectedLocalRound(block)):
                        sqldb.setLogBlock(block,1)
                        pos = block.index
                        if(pos not in self.msg_arrivals):
                            self.msg_arrivals[pos] = {}
                        self.msg_arrivals[pos][block.node] = []
                        self.msg_arrivals[pos][block.node].append(block)
                        self.msg_arrivals[pos][block.node].append(ip)
                        self.msg_arrivals[pos][block.node].append(stake)                  
                    else:
                        sqldb.changeArrivedBlock(block,2)
                        print("BLOCK IS TOO LATE! INDEX: ", block.index) 
                        print("\n\n\n") 
                
                del self.send_time[delay]
                self.semaphore.acquire()
                self.listen_signal.set()
                self.semaphore.release()
            if((float(time.mktime(datetime.datetime.now().timetuple())) - nowTime) < 1):              
                time.sleep(float(1) - (float(time.mktime(datetime.datetime.now().timetuple())) - nowTime))
            else:
                print("SEND_BLOCK EXPEND A LOT OF TIME!")
            #print("NEXT DELAY: ", int(time.mktime(datetime.datetime.now().timetuple())))            
            nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
            delay = delay + 1
            #print("DELAY: ", delay)'''
            

    '''def insertNewBlock(self,message):
        ip = message[0]
        stake = message[1]
        block = message[2]
        peers = parameter.peers
        based_time = int(time.mktime(datetime.datetime.now().timetuple()))
        #for i in peers:
        delay = based_time + self.delay()
        if(delay not in self.send_time):
            self.send_time[delay] = {}
            index = 0
        else:
            index = max(self.send_time[delay]) + 1
        #self.send_time[time][peers][index] = {}
        self.send_time[delay][index] = [ip,stake,block]'''
   
    def listen(self):
        self.bind(self.psocket)    
        while True and not self.k.is_set():            
            try:
                msg, ip, user_stake, block_recv = self.subsocket.recv_multipart()
                user_stake = int(user_stake)
                #print("NEW BLOCK FROM: ", ip)
                if(ip != self.ipaddr):
##                  self.f.clear()
##                  newChain = False 
                    #serialize
                    b = pickle.loads(block_recv)
                    print("NEW BLOCK: ", b.hash)
                    b.arrive_time = float(time.mktime(datetime.datetime.now().timetuple()))
                    ##logging.info("Got block %s miner %s" % (b.hash, ip))
                    status = self.commitBlock(message=[b.hash],t = 15)                             
                    if(not status): 
                        if(validations.validateExpectedLocalRound(b)):
                        #    print("####LISTEN####")
                        #    print("LISTEN TIME: ", int(time.mktime(datetime.datetime.now().timetuple()))) 
                        #    print("HASH BLOCk: ", b.hash)                   
                        #    print("##END LISTEN##")
                        #    #print("hash: ", b.hash)
                            pos = b.index
                            if(pos not in self.msg_arrivals):
                                self.msg_arrivals[pos] = {}

                            self.msg_arrivals[pos][b.node] = []
                            self.msg_arrivals[pos][b.node].append(b)
                            self.msg_arrivals[pos][b.node].append(ip)
                            self.msg_arrivals[pos][b.node].append(user_stake)
                            sqldb.setLogBlock(b,1) 
                        else:
                            print("BLOCK IS TOO LATE!")                        
                        sqldb.setArrivedBlock(b,1)                                                                                                                      
                        #self.insertNewBlock(message=[ip, str(user_stake), b])
                        self.semaphore.acquire()
                        self.listen_signal.set()                        
                        self.semaphore.release()                        
                        self.psocket.send_multipart([consensus.MSG_BLOCK, ip, str(user_stake), pickle.dumps(b, 2)])
                        
                    #self.semaphore.release()
##                self.f.set()

            except (zmq.ContextTerminated):
                print("problem on the zmq.Context")
            time.sleep(0.1)

 
    def listenInsert(self):
        """ Listen to block messages in a REQ/REP socket - We need to change from SUP to REQ/REP, because 
            the new version of the protocol has a variable delay and the blocks will be send on
            diferent times.
            Message frames: [ 'block', ip, block data ]
        """
        while True and not self.k.is_set():
            self.listen_signal.wait()          
            #if (self.msg_arrivals and not self.threadSync.is_set()):
            self.semaphore.acquire()
            print("CALL LISTEN FUNCTION")
            if(not self.threadSync.is_set()):                
                self.f.clear()                
                for i, msg in sorted(self.msg_arrivals.items(), key=itemgetter(1)):
                    for j, item in sorted(self.msg_arrivals[i].items(), key=itemgetter(1)):
                        b = item[0]
                        node = item[1]
                        user_stake = int(item[2])
                        print("########STARTING INSERT NEW BLOCK#########")                            
                        print("NEW BLOCK ARRIVED")
                        print(b.index)
                        print(b.hash)
                        print(b.prev_hash)
                        #print("LISTEN INSERT TIME: ", int(time.mktime(datetime.datetime.now().timetuple()))) 
                        #print("user_stake: ", user_stake)
                        if validations.validateBlockHeader(b):
                            logging.debug('valid block header')
                            prevBlock = self.commitBlock([b.prev_hash],t=14)
                            if(prevBlock and sqldb.isLeaf(b.index)):   
                                print("prev block found: ", b.prev_hash)                             
                                if(b.round > prevBlock.round):
                                    checkProof, subUser = validations.validateProofHash(b,user_stake,self.cons)
                                    if(checkProof):
                                        status = self.commitBlock(message = [b],t = 2)                                        
                                del self.msg_arrivals[i][j]
                            else:
                                nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
                                currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))
                                #print("block not has prev: ", b.hash)
                                #print("block index: ", b.index)
                                #print("block round: ", b.round)
                                #print("current round: ", currentRound)
                                if((b.round < currentRound - parameter.round_buffer) and self.firstsync == 0):
                                    #print("block removing...", b.round)
                                    #print("block currentRound...", currentRound)
                                    del self.msg_arrivals[i][j]

                        print("########END INSERT NEW BLOCK#########")
                        print("\n\n")                            
                    #if(not self.threadSync.is_set()):
                    if(not self.msg_arrivals[i]):
                        del self.msg_arrivals[i]
                    self.f.set()
                    self.e.clear()
                    #if not self.minecontrol.is_set() and self.startMine:
                    #    self.minecontrol.set()

            self.listen_signal.clear()                
            self.semaphore.release()   
            #time.sleep(0.5)   
            
    def mine(self):
        """ Create and send block in PUB socket based on consensus """
        name = threading.current_thread().getName()
        prevTime = float(parameter.GEN_ARRIVE_TIME)
        nowTime = float(time.mktime(datetime.datetime.now().timetuple())) 
        status = True           
        first = True
        while True and not self.k.is_set():
            self.start.wait()
            self.f.wait()            
            if((nowTime - prevTime) >= parameter.timeout):
                currentRound =  int(math.floor((float(time.mktime(datetime.datetime.now().timetuple()))  - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))                                
                print("CURRENT_ROUND: %d", currentRound)
                #self.semaphore.acquire()
                #self.listen_signal.set() #check if buffer has same block to insert before mine
                #time.sleep(0.1) #wait a few time to guaranteed that listen thread get the semaphore first
                #self.semaphore.release()
                if(status):        
                    self.stableBlock() #stableround

                if(not self.threadSync.is_set()):
                    if(status):
                        if(first):
                            prevTime = float(time.mktime(datetime.datetime.now().timetuple()))
                            first = False
                        else:
                            prevTime = nowTime
                        print("normal flow...")
                        print("prevTime: ", prevTime)
                    else:
                        status = True
                        prevTime = startTime
                        print("sync return...")
                        print("prevTime: ",startTime)

                    self.semaphore.acquire()
                    print("########STARTING MINE NEW BLOCK#########")
                    print("ROUND: ", currentRound)
                    self.generateNewblock(currentRound)                            
                    self.semaphore.release()

                    nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
                    print("NOWTIME: ", nowTime)
                    if(nowTime - prevTime < parameter.timeout):
                        print("sleeping time 1: ",parameter.timeout - (nowTime - prevTime))
                        time.sleep(parameter.timeout - (nowTime - prevTime))                        
                    else:
                        currentRoundTime = parameter.timeout * currentRound                
                        print("sleeping time 2: ", parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRoundTime))
                        time.sleep(parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRoundTime))
                    nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
                else:
                    if(status):
                        print("STATUS: ", status)
                        status = False
                        startTime = nowTime
                    time.sleep(1)
                    nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
                    print("NowTime: ", nowTime)
                    print("prevTime:", prevTime)

    def generateNewblock(self, round):
        """ Loop for PoS in case of solve challenge, returning new Block object """
        #r = int(math.floor((int(time.mktime(datetime.datetime.now().timetuple())) - int(lastBlock.arrive_time)) / parameter.timeout))
        #startTime = int(time.mktime(datetime.datetime.now().timetuple()))
        block = self.commitBlock(t=13)
        #self.semaphore.release()
        #print(blocks)
        #for i in blocks:
        #block = blocks[i][0]
        #print(block.index)
        while(block.round >= round):
            block = self.commitBlock([block.prev_hash], t=14)
            #self.semaphore.release()
        if(block):
            print("trying block:")
            print(block.index + 1)
            print("trying round:")
            print(round)
            replyMine, triedTime = self.commitBlock(message=[block,round],t=0)
            print("########END MINE NEW BLOCK#########")
            print("\n\n\n")
        self.e.clear()         
   
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

    def syncRequestBlockPerPeer(self,hash,peer):
        #while(index < len(peers_vote)):
        message = self.reqBlock([pickle.dumps(hash,2),'block'],peer)
        b = None
        if(message):
            message = pickle.loads(message)
            b = message            
        return b

    def syncRequestBlock(self,hash,peers_vote):
        index = 0
        while(index < len(peers_vote)):
            message = self.reqBlock([pickle.dumps(hash,2),'block'],peers_vote[index])
            index = index + 1
            b = None
            if(message):
                message = pickle.loads(message)
                b = message
                if(b):
                    #b = pickle.loads(b)
                    if(b.hash == hash):
                        return b
            return b

    #request correct block to ordered peers and all others known blocks

    #return: correct block b and list with all other round blocks
    def syncRequestAllBlocksPerPeer(self,b,peer):
        blocks = None
        index = 0
        #while(index < len(peers_vote) and vote_peers < (float(peerS) * 0.66)):
            #stake = stake + orderpeer[index][1]
        message = self.reqBlock([pickle.dumps(b,2),'allblocks'],peer)
        if(message):
            blocks = pickle.loads(message)                        
        return blocks

    def syncRequestAllBlocks(self,b,peers_vote,peerS):
        blocks = {}
        index = 0
        vote_peers = 0
        while(index < len(peers_vote)):
        #while(index < len(peers_vote) and vote_peers < (float(peerS) * 0.66)):
            #stake = stake + orderpeer[index][1]
            vote_peers = vote_peers + 1
            message = self.reqBlock([pickle.dumps(b,2),'allblocks'],peers_vote[index])
            if(message):
                block = pickle.loads(message)
                for b in block:
                    if b.hash not in blocks:
                        blocks[b.hash] = b
            index = index + 1    
        return blocks

    def syncRequestMajorPerPeer(self,round, peer):
        index = 0
        status = False
        blocks = []
        message = self.reqBlock([pickle.dumps(round,2),'majorblock'],peer)
        b = None
        #logblock = None
        if(message):
            message = pickle.loads(message)
            b = message
            #logblock = message[1]
            print("block return: ", b)
        return b

    def syncRequestMajor(self,round,orderpeer,peerS):
        index = 0
        status = False
        blocks = []
        while(not status and index < len(self.peers)):
            message = self.reqBlock([pickle.dumps(round,2),'majorblock'],orderpeer[index][0])
            b = None
            #logblock = None
            if(message):
                message = pickle.loads(message)
                b = message
                #logblock = message[1]
            print("block return: ", b)
            if(b):
                #b = pickle.loads(b)
                if(b.round == round):
                    blocks = blocks + [[b.proof_hash, orderpeer[index][0]]]
                    status, peers_vote = chaincontrol.checkMajorBlock(blocks,peerS)
                    print("status: ", status)
            index = index + 1
        if(status):
            return b, peers_vote
        else:
            return None, None

    def syncNode(self):
        while True and not self.k.is_set():
            self.threadSync.wait()
            if(self.threadSync.is_set()):
                print("\n\nSYNCING...")
                stake = parameter.numStake
                trust = parameter.trusted
                peerS = 0
                orderpeer = []
                round = self.lastRound
                for i in self.peers:
                    h = hashlib.sha256(str(i['ipaddr'])).hexdigest()            
                    #peerS = peerS + stake[1][i['ipaddr']][0]
                    #peerS = peerS + stake[1][h][0]
                    peerS = peerS + 1                    
                    index = 0
                    for j in orderpeer:
                        if j[1] >= stake[1][h][0]:
                            index = index + 1
                        else:
                            break
                    orderpeer.insert(index, [i['ipaddr'],stake[1][h][0]])
                print("sorted peer by stake: ", orderpeer)
                
                index = 0
                while(index < len(orderpeer)):
                    chain = defaultdict(list)
                    blocks = []
                    t = 0
                    log = {}
                    b = self.syncRequestMajorPerPeer(round - parameter.roundTolerancy - 1, orderpeer[index][0])                
                    if(b):
                        print("proof_hash first block sync function: ", b.proof_hash)
                        #inserting block on chain
                        # 1-block request by network
                        chain[t].append(b)

                        #get all know blocks that have same prev_hash                        
                        blocks = self.syncRequestAllBlocksPerPeer(b, orderpeer[index][0])
                        if(blocks):
                            log[t] = []
                            #for item in blocks:
                            #log[t] = log[t] + [blocks[item]]
                            log[t] = blocks

                        #we have here the major of nodes choosing the block b
                        #now node check if is possible build the chain until this block.
                        #first we need to check if the node has prev_block on log_block table.
                        #Next, if node not has the prev_block, it necessary send a new request to peers
                        prev_hash = b.prev_hash
                        status = True
                        #r = b.round
                        #self.semaphore.acquire()
                        r = b.round
                        while(status and not sqldb.dbKnowBlock(prev_hash)):
                            status = False
                            #trying get block in log_block table
                            b = sqldb.getLogBlock(prev_hash)
                            if(b):
                                if(b.round < r):
                                    t = t + 1
                                    r = b.round
                                    chain[t].append(b)
                                    prev_hash = b.prev_hash
                                    status = True
                            else:                            
                                b = self.syncRequestBlockPerPeer(prev_hash, orderpeer[index][0])
                                if(b and b.round < r):
                                    t = t + 1
                                    r = b.round
                                    chain[t].append(b)
                                    prev_hash = b.prev_hash
                                    status = True

                            if not status:
                                chain = None
                                break

                            #get all know blocks that have same prev_hash
                            blocks = self.syncRequestAllBlocksPerPeer(b, orderpeer[index][0])
                            if(blocks):
                                log[t] = []
                                #for item in blocks:
                                #log[t] = log[t] + [blocks[item]]
                                log[t] = blocks
                        lastround = r
                        if(chain):                       
                            ######insert all blocks. More blocks node knows better######
                            t = max(chain)
                            sumsuc = 0
                            while t >= 0:
                                blocks = None                            
                                if(t in log):
                                    blocks = log[t]
                                    s,suc = self.commitBlock(message = [blocks], t=16)
                                    sumsuc = sumsuc + suc
                                t = t - 1
                            ############end insert new blocks on log_block#############
                            
                            #############check all blocks in the chain################
                            t = max(chain)
                            checkProof = False
                            while t >= 0:                            
                                b = chain[t][0]
                                checkProof, subUser = validations.validateProofHash(b,stake[1][b.node][0],self.cons)
                                if(not checkProof):
                                    break
                                t = t - 1
                            #############end check all blocks in the chain#############

                            
                            #if node know head block we have nothing to do: new chain is the same
                            b = chain[0][0]
                            know = sqldb.dbKnowBlock(b.hash)
                            print("know: ", know)                      
                            calculation.newReversion(self,round,lastround)
                            if(not know and checkProof): 
                                #insert new unsync identification in the log file                                                   
                                self.semaphore.acquire() 
                                #check if new chain has a better s than current chain
                                bestchain = True
                                if(self.firstsync == 0):
                                    currentsuc = sqldb.getCurrentSuc(lastround,(round-parameter.roundTolerancy-1))
                                    print("current suc: ", currentsuc)
                                    mnew = float(sumsuc) / (((round-parameter.roundTolerancy-1) - lastround) + 1)
                                    mcurrent = float(currentsuc) / (((round-parameter.roundTolerancy-1) - lastround) + 1)
                                    if(mnew <= mcurrent):
                                        bestchain = False
                                    print("new sum suc: ", sumsuc)
                                    print("interval: ",(((round-parameter.roundTolerancy-1) - lastround) + 1))
                                    print("initialround: ", lastround)
                                    print("lastround: ", (round-parameter.roundTolerancy-1))
                                    print("new mean: ", mnew)
                                    print("current mean: ", mcurrent)
                                ##############end check new chain s#################                            
                                if(bestchain):
                                    fblock = chain[max(chain)][0]
                                    lblock = chain[0][0]
                                    calculation.calcReversionLenght(self,fblock,lblock) 
                                    t = max(chain) 
                                    b = chain[t][0]                                
                                    if(sqldb.dbKnowBlock(b.prev_hash)):                                
                                        #remove all block that were inserted in rounds higher than sync round.
                                        #this blocks can be created or received before unsync discovery
                                        #start on currentRound                        
                                        r =  int(math.floor((float(time.mktime(datetime.datetime.now().timetuple())) - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))
                                        while(r >= round - parameter.roundTolerancy):
                                            sqldb.removeBlock(r)
                                            r = r - 1                       

                                        while t >= 0:
                                            b = chain[t][0]
                                            if(b):    
                                                sqldb.setArrivedBlock(b,1)    
                                                sqldb.setLogBlock(b,1)
                                                sqldb.removeBlock(b.index)                                                
                                                idChain = sqldb.getIdChain(b.prev_hash)
                                                sqldb.writeChainLeaf(idChain,b)                                    
                                            t = t - 1  
                                    #self.resync = 2                                                                                                                 
                                    self.semaphore.release()
                                else:
                                    calculation.endwithoutreversion(self)
                                    self.semaphore.release()
                                    print("PEERS HAVE A WORST CHAIN...WE WILL NEED CONNECT WITH MORE PEERS AND TRY AGAIN")                
                                    #self.resync = self.resync + 1
                            else:
                                calculation.endwithoutreversion(self)
                                #self.semaphore.release()
                                print("PEERS BELIEVE ON THE SAME CHAIN OR CHAIN IS NOT CORRECT.")
                                #self.resync = self.resync + 1                                                        
                        else:
                            #self.semaphore.release()
                            print("PEERS CHAIN IS NOT CORRECT")
                            #self.resync = self.resync + 1              
                    else:
                        #self.semaphore.release()
                        print("PEERS NOT HAVE CONSENSUS IN A COMMON BLOCK.")
                        #self.resync = self.resync + 1

                    index = index + 1
                    
            #self.start.clear()             
            if(self.firstsync == 1):
                self.firstsync = 0
            self.semaphore.acquire()
            self.listen_signal.set() #check if buffer has same block that was received after sync.
            self.semaphore.release()
            print("END SYNC \n\n")
            self.threadSync.clear()                                
            
    def sync(self):
        while True and not self.k.is_set():
            self.threadSync.wait()
            if(self.threadSync.is_set()):
                print("\n\nSYNCING...")
                t = 0
                chain = defaultdict(list)
                log = {}
                stake = parameter.numStake
                trust = parameter.trusted
                blocks = []
                print("numStake: ", stake)
                #calc neighboor stake
                peerS = 0
                orderpeer = []
                round = self.lastRound
                for i in self.peers:
                    h = hashlib.sha256(str(i['ipaddr'])).hexdigest()            
                    #peerS = peerS + stake[1][i['ipaddr']][0]
                    #peerS = peerS + stake[1][h][0]
                    peerS = peerS + 1                    
                    index = 0
                    for j in orderpeer:
                        if j[1] >= stake[1][h][0]:
                            index = index + 1
                        else:
                            break
                    orderpeer.insert(index, [i['ipaddr'],stake[1][h][0]])
                print("sorted peer by stake: ", orderpeer)
                
                #requestBlock to peers on the higher stable round
                if(self.firstsync == 1):
                    b, peers_vote = self.syncRequestMajor(round,orderpeer,peerS)
                else:
                    b, peers_vote = self.syncRequestMajor(round - parameter.roundTolerancy - 1,orderpeer,peerS)
                    #b = self.syncRequestMajor(round - parameter.roundTolerancy - 1,orderpeer,peerS)
                #######if syncRequestMajor return one block peers deal is ok ###############
                if(b):
                    print("proof_hash first block sync function: ", b.proof_hash)
                    #inserting block on chain
                    # 1-block request by network
                    chain[t].append(b)

                    #get all know blocks that have same prev_hash
                    blocks = self.syncRequestAllBlocks(b, peers_vote, peerS)
                    if(blocks):
                        log[t] = []
                        for item in blocks:
                            log[t] = log[t] + [blocks[item]]

                    #we have here the major of nodes choosing the block b
                    #now node check if is possible build the chain until this block.
                    #first we need to check if the node has prev_block on log_block table.
                    #Next, if node not has the prev_block, it necessary send a new request to peers
                    prev_hash = b.prev_hash
                    status = True
                    r = b.round
                    #self.semaphore.acquire()
                    while(status and not sqldb.dbKnowBlock(prev_hash)):
                        
                        status = False
                        #trying get block in log_block table
                        b = sqldb.getLogBlock(prev_hash)
                        if(b):
                            if(b.round < r):
                                t = t + 1
                                r = b.round
                                chain[t].append(b)
                                prev_hash = b.prev_hash
                                status = True
                        else:                            
                            b = self.syncRequestBlock(prev_hash,peers_vote)
                            if(b and b.round < r):
                                t = t + 1
                                r = b.round
                                chain[t].append(b)
                                prev_hash = b.prev_hash
                                status = True

                        if not status:
                            chain = None
                            break

                        #get all know blocks that have same prev_hash
                        blocks = self.syncRequestAllBlocks(b, peers_vote, peerS)
                        if(blocks):
                            log[t] = []
                            for item in blocks:
                                log[t] = log[t] + [blocks[item]]
                    lastround = r
                    if(chain):                       
                        ######insert all blocks. More blocks node knows better######
                        t = max(chain)
                        sumsuc = 0
                        while t >= 0:
                            blocks = None                            
                            if(t in log):
                                blocks = log[t]
                                s,suc = self.commitBlock(message = [blocks], t=16)
                                sumsuc = sumsuc + suc
                            t = t - 1
                        ############end insert new blocks on log_block#############
                        
                        #############check all blocks in the chain################
                        t = max(chain)
                        checkProof = False
                        while t >= 0:                            
                            b = chain[t][0]
                            checkProof, subUser = validations.validateProofHash(b,stake[1][b.node][0],self.cons)
                            if(not checkProof):
                                break
                            t = t - 1
                        #############end check all blocks in the chain#############

                        
                        #if node know head block we have nothing to do: new chain is the same
                        b = chain[0][0]
                        know = sqldb.dbKnowBlock(b.hash)
                        print("know: ", know)                      
                        calculation.newReversion(self,round,lastround)
                        if(not know and checkProof): 
                            #insert new unsync identification in the log file                                                   
                            self.semaphore.acquire() 
                            #check if new chain has a better s than current chain
                            bestchain = True
                            if(self.firstsync == 0):
                                currentsuc = sqldb.getCurrentSuc(lastround,(round-parameter.roundTolerancy-1))
                                print("current suc: ", currentsuc)
                                mnew = float(sumsuc) / (((round-parameter.roundTolerancy-1) - lastround) + 1)
                                mcurrent = float(currentsuc) / (((round-parameter.roundTolerancy-1) - lastround) + 1)
                                if(mnew <= mcurrent):
                                    bestchain = False
                                print("new sum suc: ", sumsuc)
                                print("interval: ",(((round-parameter.roundTolerancy-1) - lastround) + 1))
                                print("initialround: ", lastround)
                                print("lastround: ", (round-parameter.roundTolerancy-1))
                                print("new mean: ", mnew)
                                print("current mean: ", mcurrent)
                            ##############end check new chain s#################                            
                            if(bestchain):
                                fblock = chain[max(chain)][0]
                                lblock = chain[0][0]
                                calculation.calcReversionLenght(self,fblock,lblock) 
                                t = max(chain) 
                                b = chain[t][0]                                
                                if(sqldb.dbKnowBlock(b.prev_hash)):                                
                                    #remove all block that were inserted in rounds higher than sync round.
                                    #this blocks can be created or received before unsync discovery
                                    #start on currentRound                        
                                    r =  int(math.floor((float(time.mktime(datetime.datetime.now().timetuple())) - float(parameter.GEN_ARRIVE_TIME))/ parameter.timeout))
                                    while(r >= round - parameter.roundTolerancy):
                                        sqldb.removeBlock(r)
                                        r = r - 1                       

                                    while t >= 0:
                                        b = chain[t][0]
                                        if(b):    
                                            sqldb.setArrivedBlock(b,1)    
                                            sqldb.setLogBlock(b,1)
                                            sqldb.removeBlock(b.round)
                                            idChain = sqldb.getIdChain(b.prev_hash)
                                            sqldb.writeChainLeaf(idChain,b)                                    
                                        t = t - 1  
                                self.resync = 2                                                                                                                 
                                self.semaphore.release()
                            else:
                                calculation.endwithoutreversion(self)
                                self.semaphore.release()
                                print("PEERS HAVE A WORST CHAIN...WE WILL NEED CONNECT WITH MORE PEERS AND TRY AGAIN")                
                                self.resync = self.resync + 1
                        else:
                            calculation.endwithoutreversion(self)
                            #self.semaphore.release()
                            print("PEERS BELIEVE ON THE SAME CHAIN OR CHAIN IS NOT CORRECT.")
                            self.resync = self.resync + 1                                                        
                    else:
                        #self.semaphore.release()
                        print("PEERS CHAIN IS NOT CORRECT")
                        self.resync = self.resync + 1              
                else:
                    #self.semaphore.release()
                    print("PEERS NOT HAVE CONSENSUS IN A COMMON BLOCK.")
                    self.resync = self.resync + 1
                    
            #self.start.clear()             
            if(self.resync >= 1):        
                if(self.firstsync == 1):
                    self.firstsync = 0
                self.semaphore.acquire()
                self.listen_signal.set() #check if buffer has same block that was received after sync.
                #time.sleep(1)
                self.semaphore.release()
                print("END SYNC \n\n")
                self.threadSync.clear()                                

            else:
                peers = parameter.peers
                if((len(peers) - 1) > len(self.connectPeers)):                                    
                    reconnectT = len(self.connectPeers) + 1
                    self.neighbors(ipaddr=self.ipaddr,firstC=False,pPeers=reconnectT)  
                
                self.semaphore.acquire()
                self.listen_signal.set()                 
                self.semaphore.release()
                self.threadSync.clear()
                
    '''def insertChain(self,k,chain):
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
        return False'''
  
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
            if(messages[0].lower() == consensus.MSG_REQBLOCK and self.threadSync.is_set()):
                reply = None
            #reply = self.commitBlock(message=messages,t=10)
            else:
                reply = consensus.handleMessages(self.bchain, messages,self)
            #self.semaphore.release()
            self.repsocket.send_multipart([self.ipaddr, pickle.dumps(reply, 2)])
    def rpcServer(self, ip='127.0.0.1', port=9999):
        """ RPC-like server to interact with rpcclient.py """
        self.bind(self.rpcsocket,port=port)
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
            elif cmd == rpc.MSG_SHOWPEERS:
                p = []
                for item in self.peers:
                    p = p + [item['ipaddr']]
                self.rpcsocket.send_pyobj(p)
            elif cmd == rpc.MSG_CONNECT:
                self.rpcsocket.send_string('Starting neighbor connect...')
                #thread that control neighbors connecting
                msg_start_peers = threading.Thread(name='neighbors', target=self.neighbors, kwargs={'ipaddr':self.ipaddr})
                msg_start_peers.start()
                self.threads.append(msg_start_peers)
            elif cmd == rpc.MSG_STAKE:
                self.rpcsocket.send_string('setting node stake...')
                stake = messages[1]
                self.setStake(stake)                  
            elif cmd == rpc.MSG_START:
                self.rpcsocket.send_string('Starting mining...')
                nowTime = float(time.mktime(datetime.datetime.now().timetuple()))
                currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME)) / parameter.timeout))                    
                if(not self.startMine):
                    self.miner_thread = threading.Thread(name='Miner', target=self.mine)
                    self.threads.append(self.miner_thread)
                    self.startMine = True

                    #current round time
                    self.startround = currentRound + 1
                    self.miner_thread.start()
                
                #current round time
                currentRound =  int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME)) / parameter.timeout))                    
                currentRound = parameter.timeout * currentRound                
                print("Sleeping time: ", parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound))
                time.sleep(parameter.timeout - ((nowTime - parameter.GEN_ARRIVE_TIME) - currentRound))                
                self.start.set()
                #self.minecontrol.set()
                self.f.set()
                self.e.clear()
            elif cmd == rpc.MSG_STOP:
                lock = True
                #while(lock):
                    #if(not self.e.is_set()):
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
    def peeringRequest(self, salt, address):
        m = None
        if address:
            self.restart()
            print("peering ipaddress: ", address)
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            #print("IP")
            #print(address)
            time.sleep(3)
            try:
                self.router.send_multipart([consensus.MSG_REQPEER,str(salt),self.ipaddr])
                m = self._poll(self.router)[0]
            except Exception as e:
                print(str(e))                
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        return m

    def reqBlock(self, message, address = None):
        m = None
        if address:
            self.restart()
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            print("IP")
            print(address)

            #time.sleep(0.2)
            try:
                self.router.send_multipart([consensus.MSG_REQBLOCK,message[0],str(message[1])])
                m = self._poll(self.router)[0]
            except Exception as e:
                print(str(e))
                
            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        else:
            try:
                self.reqsocket.send_multipart([consensus.MSG_REQBLOCK,str(round)])
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
    parser.add_argument('-sy', '--sync', metavar='sync', dest='sync',
                        help='Specify first sync', default=0)    
    parser.add_argument('--stake', dest='stake', nargs='*',
                        help='Specify stake user', default=[])
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
    cfgparser = SafeConfigParser({'ip': args.ipaddr, 'port': str(args.port),'sync':args.sync,'stake':args.stake,'peers': args.peers, 'miner': str(args.miner).lower(), 'loglevel': 'warning', 'diff': '5'})
    if cfgparser.read(args.config_file):
        args.peers = cfgparser.get('node','ip')
        args.port = int(cfgparser.get('node','port'))
        args.sync = int(cfgparser.get('node','sync'))
        args.stake = cfgparser.get('node','stake').split('\n')
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
    
    
    #n = Node(args.ipaddr, args.port)
    print("args.ipaddr:", args.ipaddr)
    print("args.port:",args.port)
    n = Node(args.ipaddr, args.port)
    n.threads = []
    n.setCons(cons)
    # Connect to predefined peers
    if args.peers:
        iplist = args.peers if isinstance(args.peers, list) else [args.peers]
        for ipaddr in iplist:
            n.addPeer(ipaddr)
    
    else: # Connect to localhost
        logging.info('Connecting to localhost...')
        n.connect()
    time.sleep(1)

    if(args.sync):
        print("firstsync: ", args.sync)
        n.setFirstSync(args.sync)

    #get stake as a list 
    if args.stake:
        stakeList = args.stake if isinstance(args.stake, list) else [args.stake]
        n.setStake(stakeList[0])
   

    # Connect and check own node database
    logging.info('checking database')
    sqldb.dbConnect()
    n.bchain = sqldb.dbCheck()
    sqldb.dbInsertFirstBlock()
    
    msg_thread = threading.Thread(name='REQ/REP', target=n.messageHandler)
    msg_thread.start()
    n.threads.append(msg_thread)

    # Thread to listen broadcast messages
    #listen_thread = threading.Thread(name='PUB/SUB', target=n.listen)
    #listen_thread.start()
    #n.threads.append(listen_thread)    

    #listenInsert_thread = threading.Thread(name='listenInsert', target=n.listenInsert)
    #listenInsert_thread.start()
    #n.threads.append(listenInsert_thread)
        
    # Thread to Sync node
    #sync_thread = threading.Thread(name='sync', target=n.syncNode)
    #sync_thread.start()
    #n.threads.append(sync_thread)
          
        
    # Miner thread    
    if args.miner:
        n.miner_thread = threading.Thread(name='Miner', target=n.mine)
        n.threads.append(n.miner_thread)
        n.miner_thread.start()
        n.start.set()
        n.f.set()

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
