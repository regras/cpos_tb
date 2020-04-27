from leaf import Leaf
from collections import defaultdict
import json
import time
import datetime
import parameter
import sqldb
import threading
class Leafchain:
    def __init__(self, db=None):

        self.indexMainChain = 0
        self.roundMainChain = 0
        self.hashMainChain = 0
        self.prevIndexMainChain = -1
        self.prevRoundMainChain = 0
        self.prevHashMainChain = 0
        self.lastArrivedTime = parameter.GEN_ARRIVE_TIME
        self.lastRound = 0
        self.leaf = defaultdict(list)
        self.semaphore = threading.Semaphore()

        if db:
            # order in database definition
            l = db if isinstance(db, Leaf) else Leaf(leaf_node=db[4],leaf_index=db[0],leaf_head=db[8],leaf_prev_head=db[9],
            leaf_bhash=db[3], leaf_round=db[1],leaf_arrivedTime=db[7],leaf_prev_hash=db[10],leaf_prev_round=db[11],
            leaf_prev_arrivedTime=db[12],leaf_prev2_hash=db[13],leaf_prev2_round=db[14],
            leaf_prev2_arrivedTime=db[15],lastId=db[0])
            self.leaf[0].append(l)

            block = sqldb.dbtoBlock(sqldb.blockHashQuery(l.leaf_hash))
            self.UpdateMainChain(block)    
            
        else:
            l = Leaf(0,"",1,"",parameter.GEN_ARRIVE_TIME)
            self.leaf[0].append(l)

            self.indexMainChain = 0
            self.roundMainChain = 1
            self.hashMainChain = l.leaf_hash
            self.prevIndexMainChain = -1
            self.prevRoundMainChain = 0
            self.prevHashMainChain = l.leaf_hash

       
    def setLastArrivedTime(self,arrive_time):
        self.lastArrivedTime = arrive_time

    def setLastRound(self,round):
        self.lastRound = round
            
    def getLenLeaf(self):
        return (len(self.leaf)) 

    def getLeafs(self):
        self.semaphore.acquire()
        return self.leaf

    def releaseSemaphore(self):
        self.semaphore.release()

    def getLastArrivedTime(self):
        return self.lastArrivedTime
    
    def getRoundMainChain(self):
        return self.roundMainChain
    
    def getIndexMainChain(self):
        return self.indexMainChain
    
    def getArriveTime(self,k):
        return self.leaf[k][0].leaf_arrivedTime
    
    #def getElementByPosition(self,pos):
    #    if(pos < self.getLenLeaf()):
    #        return self.leaf[pos][0] 
    
    def getMainChain(self):
            return self.roundMainChain, self.indexMainChain, self.prevRoundMainChain, self.prevIndexMainChain

    def appendLeaf(self,db):
        l = db if isinstance(db, Leaf) else Leaf(leaf_node=db[4],leaf_index=db[0],leaf_head=db[8],leaf_prev_head=db[9],
        leaf_bhash=db[3], leaf_round=db[1],leaf_arrivedTime=db[7],leaf_prev_hash=db[10],leaf_prev_round=db[11],
        leaf_prev_arrivedTime=db[12],leaf_prev2_hash=db[13],leaf_prev2_round=db[14],
        leaf_prev2_arrivedTime=db[15],lastId=db[0],subuser=db[18])
        self.leaf[max(self.leaf)+1].append(l)
        if(l.leaf_index > self.indexMainChain):
            block = sqldb.dbtoBlock(sqldb.blockHashQuery(l.leaf_hash))
            self.UpdateMainChain(block)    
    
    def removeLeaf(self,pos):
        print("remove chain with head")
        print(self.leaf[pos][0].leaf_head)
        print("remove chain with prev_head")
        print(self.leaf[pos][0].leaf_prev_head)
        print("index")
        print(self.leaf[pos][0].leaf_index)
        print("hash")
        print(self.leaf[pos][0].leaf_hash)
        #sqldb.setLogFork(self.leaf[pos][0].leaf_head,'0')
        #sqldb.setLogFork(self.leaf[pos][0].leaf_head, 0, 0, 0, self.leaf[pos][0].leaf_index, self.leaf[pos][0].leaf_hash)
        status = sqldb.removeChain(self.leaf[pos][0].leaf_hash)
        if(status):
            print("chain removed with success")
            del self.leaf[pos]
        else:
            print("chain not removed with success. Fork point not found.")
        
    
    def IsLeaf(self, block_hash):
        for k, l in self.leaf.iteritems():
            if(block_hash == l[0].leaf_hash):
                return True
        return False
        
    def updateLeaf(self, block):
        for k,l in list(self.leaf.iteritems()):
            if(self.leaf[k][0].leaf_index >= block.index and block.hash != self.leaf[k][0].leaf_hash):
                firstIndex = sqldb.bournChain(self.leaf[k][0].leaf_head)
                print("firstIndex")
                print(firstIndex)
                if(firstIndex >=0):
                    if(firstIndex >= block.index):
                        self.removeLeaf(k)
                        #del self.leaf[k]
                    else:
                        print("Index chain to remove")
                        print(self.leaf[k][0].leaf_index)
                        numBlocksRemove = self.leaf[k][0].leaf_index - block.index
                        print("numBlocksRemove")
                        print(numBlocksRemove)
                        prev_hash = self.leaf[k][0].leaf_prev_hash
                        sqldb.removeBlock(self.leaf[k][0].leaf_hash)
                        while(numBlocksRemove >= 0):
                            new_block_leaf = sqldb.blockHashQuery(prev_hash)
                            if(numBlocksRemove > 0):
                                sqldb.removeBlock(new_block_leaf[3])
                                prev_hash = new_block_leaf[2]

                            numBlocksRemove = numBlocksRemove - 1


                        self.leaf[k][0].leaf_prev2_round = new_block_leaf[14]
                        self.leaf[k][0].leaf_prev2_hash = new_block_leaf[13]
                        self.leaf[k][0].leaf_prev2_arrivedTime = new_block_leaf[15]

                        self.leaf[k][0].leaf_prev_round = new_block_leaf[11]
                        self.leaf[k][0].leaf_prev_hash = new_block_leaf[10]
                        self.leaf[k][0].leaf_prev_arrivedTime = new_block_leaf[12]

                        self.leaf[k][0].leaf_round = new_block_leaf[1]
                        self.leaf[k][0].leaf_hash = new_block_leaf[3]
                        self.leaf[k][0].leaf_index = new_block_leaf[0]
                        self.leaf[k][0].leaf_arrivedTime = new_block_leaf[7]
                        self.leaf[k][0].leaf_lastTimeTried = self.leaf[k][0].leaf_arrivedTime

                        print("Index chain to remove after")
                        print(self.leaf[k][0].leaf_index)

        
            #if(self.leaf[k][0].leaf_round > block.round):
            #    prev_block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',self.leaf[k][0].leaf_prev_hash]))
            #    sqldb.removeBlock(['',self.leaf[k][0].leaf_hash])
            #    if(prev_block):
            #        if(not self.IsLeaf(prev_block.hash) and (prev_block.hash != block.prev_hash)):

            #            new_prev2_block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',prev_block.prev_hash]))
            #            if(new_prev2_block):
            #                self.leaf[k][0].leaf_prev2_round = new_prev2_block.round
            #                self.leaf[k][0].leaf_prev2_hash = new_prev2_block.hash
            #                self.leaf[k][0].leaf_prev2_arrivedTime = new_prev2_block.arrive_time

            #                self.leaf[k][0].leaf_prev_round = self.leaf[k][0].leaf_prev2_round 
            #                self.leaf[k][0].leaf_prev_hash = self.leaf[k][0].leaf_prev2_hash
            #                self.leaf[k][0].leaf_prev_arrivedTime = self.leaf[k][0].leaf_prev2_arrivedTime

            #                self.leaf[k][0].leaf_round = prev_block.round
            #                self.leaf[k][0].leaf_hash = prev_block.hash
            #                self.leaf[k][0].leaf_prev_hash = prev_block.prev_hash
            #                self.leaf[k][0].leaf_index = prev_block.index
            #               self.leaf[k][0].leaf_arrivedTime = prev_block.arrive_time
            #        else:
            #            del self.leaf[k]
        #print (self.leaf)        
       
    def addBlockLeaf(self,pos=None, block=None, sync=False, prevHead=None):
        #inserting block on the chain's top
        if(not sync):
            if(self.leaf[pos][0].leaf_hash == block.prev_hash and not sync):
                if(self.indexMainChain < block.index):
                    #print("indexMainChain < block.index")
                    #print("Next Block")
                    #print("last hash on leaf")
                    #print(self.leaf[pos][0].leaf_hash)
                    #print("Block prev hash")
                    #print(block.prev_hash)

                    self.UpdateMainChain(block)

                    self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                    self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                    self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                    self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                    self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                    self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                    self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                    self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried

                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time
                    self.leaf[pos][0].leaf_node = block.node

                    return self.leaf[pos][0] 

                #late block
                elif(self.indexMainChain > block.index):
                    if(block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index):

                        #print("indexMainChain > block.index")
                        #print("block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index")
                        #print("Next Block")
                        #print("last hash on leaf")
                        #print(self.leaf[pos][0].leaf_hash)
                        #print("Block prev hash")
                        #print(block.prev_hash)

                        self.UpdateMainChain(block)     

                        self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                        self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                        self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                        self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                        self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                        self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                        self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                        self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 
                                
                        self.leaf[pos][0].leaf_round = block.round
                        self.leaf[pos][0].leaf_hash = block.hash
                        self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                        self.leaf[pos][0].leaf_index = block.index
                        self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                        self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time
                        self.leaf[pos][0].leaf_node = block.node

                        self.updateLeaf(block)
                        #print("block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index")
                        #print(self.leaf)
                        return self.leaf[pos][0]

                    elif(block.round == self.prevRoundMainChain and self.prevIndexMainChain == block.index):

                        #print("prevIndexMainChain == block.index")
                        #print("block.round == self.prevRoundMainChain")
                        #print("last hash on leaf")
                        #print(self.leaf[pos][0].leaf_hash)
                        #print("Block prev hash")
                        #print(block.prev_hash)

                        self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                        self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                        self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                        self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                        self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                        self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                        self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                        self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 

                        self.leaf[pos][0].leaf_round = block.round
                        self.leaf[pos][0].leaf_hash = block.hash
                        self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                        self.leaf[pos][0].leaf_index = block.index
                        self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                        self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time

                        self.leaf[pos][0].leaf_node = block.node
                        return self.leaf[pos][0]

                                
                    else:
                        return None

                elif(self.indexMainChain == block.index):

                    if(block.round == self.roundMainChain):
                        #print("RODADA IGUAL")
                        self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                        self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                        self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                        self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                        self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                        self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                        self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                        self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 

                        self.leaf[pos][0].leaf_round = block.round
                        self.leaf[pos][0].leaf_hash = block.hash
                        self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                        self.leaf[pos][0].leaf_index = block.index
                        self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                        self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time

                        self.leaf[pos][0].leaf_node = block.node
                        return self.leaf[pos][0]

                    elif(block.round < self.roundMainChain):
                        #print("RODADA MENOR")
                        self.UpdateMainChain(block) 

                        self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                        self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                        self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                        self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                        self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                        self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                        self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                        self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 

                        self.leaf[pos][0].leaf_round = block.round
                        self.leaf[pos][0].leaf_hash = block.hash
                        self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                        self.leaf[pos][0].leaf_index = block.index
                        self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                        self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time

                        self.leaf[pos][0].leaf_node = block.node

                        self.updateLeaf(block)
                        #print("block.round < self.roundMainChain")
                        #print(self.leaf)
                        return self.leaf[pos][0]
                    else:
                        return None

            elif(self.leaf[pos][0].leaf_prev_hash == block.prev_hash and self.leaf[pos][0].leaf_index == block.index and not sync):
                print("POSSIVEL NOVO FORK")
                
                if (block.round > self.leaf[pos][0].leaf_round):
                    print("Round Maior")
                    return None
                
                elif(block.round < self.leaf[pos][0].leaf_round):

                    
                    print("Round Menor")
                    #new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash=block.prev_hash,
                    #leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                    #leaf_prev_head=self.leaf[pos][0].leaf_prev_head, leaf_head=self.leaf[pos][0].leaf_head, leaf_round=block.round,
                    #leaf_prev_round=self.leaf[pos][0].leaf_prev_round,leaf_prev2_round=self.leaf[pos][0].leaf_prev2_round, 
                    #leaf_prev_arrivedTime=self.leaf[pos][0].leaf_prev_arrivedTime, leaf_prev2_hash=self.leaf[pos][0].leaf_prev2_hash,
                    #leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev2_arrivedTime)

                    #self.leaf[max(self.leaf)+1].append(new_leaf)
                    sqldb.removeBlock(self.leaf[pos][0].leaf_hash)
                    
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                    self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time
                    self.leaf[pos][0].leaf_node = block.node
                    sqldb.writeChainLeaf(self.leaf[pos][0],block)
                    self.UpdateMainChain(block)
                    self.updateLeaf(block)
                    #print("block.round < self.leaf[pos][0].leaf_round")
                    #print(self.leaf)
                    
                    return None
                    
                   

                    
                    #sqldb.setLogFork(self.leaf[pos][0].leaf_head,'1')

                else:
                    print("Round Igual")
                    #hash1 = self.leaf[pos][0].leaf_hash
                    #hash2 = block.hash

                    #sqldb.writeChainLeaf(new_leaf,block)

                    sqldb.setForkFromBlock(self.leaf[pos][0].leaf_prev_hash)

                    #sqldb.setLogFork(self.leaf[lenght][0].leaf_head,self.leaf[lenght][0].leaf_arrivedTime,1,self.leaf[lenght][0].leaf_index,0,None,hash1,hash2)

                    new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash="",
                    leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                    leaf_prev_head=self.leaf[pos][0].leaf_head, leaf_head=block.hash, leaf_round=block.round,
                    leaf_prev_round=block.round,leaf_prev2_round=block.round, 
                    leaf_prev_arrivedTime=block.arrive_time,
                    leaf_prev2_arrivedTime = block.arrive_time)

                    lenght = max(self.leaf) + 1
                    self.leaf[lenght].append(new_leaf)
                    #print("block.round == self.leaf[pos][0].leaf_round")
                    #print(self.leaf)
            
                    return new_leaf
                #print("NOVA CHAIN")
                #print("hash na atual Leaf")
                #print(self.leaf[pos][0].head)
                #print("Head da nova Leaf")
                #print(block.hash)
                #print("prev2_arrivedTime novo")
                #print(self.leaf[pos][0].prev2_arrivedTime)

        
                return None
            elif(self.leaf[pos][0].leaf_prev2_hash == block.prev_hash and self.leaf[pos][0].leaf_index == block.index - 1 and not sync):

                print("POSSIVEL NOVO FORK NO PREV2_ROUND")
                if (block.round > self.leaf[pos][0].leaf_prev_round):
                    print("Round Maior")
                    return None

                elif(block.round < self.leaf[pos][0].leaf_prev_round):

                    print("Round Menor")
                    prev3Block = sqldb.getPrev3Block(block.prev_hash)
                    if(prev3Block):
                        prev2_arrivedTime = prev3Block[2]
                        prev2_round = prev3Block[0]
                        prev2_hash = prev3Block[1]
                    else:
                        prev2_arrivedTime = leaf[pos][0].leaf_prev2_arrivedTime
                        prev2_round = leaf[pos][0].leaf_prev2_round
                        prev2_hash = block.prev_hash
                    #new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash=block.prev_hash,
                    #leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                    #leaf_prev_head=self.leaf[pos][0].leaf_prev_head, leaf_head=self.leaf[pos][0].leaf_head, leaf_round=block.round,
                    #leaf_prev_round=self.leaf[pos][0].leaf_prev_round,leaf_prev2_round=block.round, 
                    #leaf_prev_arrivedTime=self.leaf[pos][0].leaf_prev_arrivedTime, leaf_prev2_hash=prev2_hash,
                    #leaf_prev2_arrivedTime = block.arrive_time)

                    #self.leaf[max(self.leaf)+1].append(new_leaf)
                    sqldb.removeBlock(self.leaf[pos][0].leaf_hash)
                    sqldb.removeBlock(self.leaf[pos][0].leaf_prev_hash)

                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                    self.leaf[pos][0].leaf_node = block.node

                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_prev_round = leaf[pos][0].leaf_prev2_round
                    self.leaf[pos][0].leaf_prev_arrivedTime = leaf[pos][0].leaf_prev2_arrivedTime
                    
                    self.leaf[pos][0].leaf_prev2_hash = prev2_hash
                    self.leaf[pos][0].leaf_prev2_round = prev2_round
                    self.leaf[pos][0].leaf_prev2_arrivedTime = prev2_arrivedTime
                    self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                    self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried
                    self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time

                    sqldb.writeChainLeaf(self.leaf[pos][0],block)

                    self.UpdateMainChain(block)
                    self.updateLeaf(block)

                    #sqldb.writeChainLeaf(new_leaf,block)
                    #print("block.round < self.leaf[pos][0].leaf2_round")
                    #print(self.leaf)
                    return None
                    
                else:
                    print("Round Igual")
                    hash1 = self.leaf[pos][0].leaf_prev_hash
                    hash2 = block.hash

                    #sqldb.writeChainLeaf(new_leaf,block)
                    
                    sqldb.setForkFromBlock(self.leaf[pos][0].leaf_prev2_hash)
                
                    #sqldb.setLogFork(self.leaf[lenght][0].leaf_head,self.leaf[lenght][0].leaf_arrivedTime,1,self.leaf[lenght][0].leaf_index,0,None,hash1,hash2)

                    new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash="",
                    leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                    leaf_prev_head=self.leaf[pos][0].leaf_head, leaf_head=block.hash, leaf_round=block.round,
                    leaf_prev_round=block.round,leaf_prev2_round=block.round, 
                    leaf_prev_arrivedTime=block.arrive_time,
                    leaf_prev2_arrivedTime = block.arrive_time)

                    lenght = max(self.leaf) + 1
                    self.leaf[lenght].append(new_leaf)
                    #print("block.round == self.leaf[pos][0].leaf_prev2_round")
                    #print(self.leaf)

                    return new_leaf


                return None

        elif(sync):
            if(pos == -1):
                print("New Chain - Fork after sync function")

                sqldb.setForkFromBlock(block.prev_hash)            
            
                new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash="",
                leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                leaf_prev_head=prevHead, leaf_head=block.hash, leaf_round=block.round,
                leaf_prev_round=block.round,leaf_prev2_round=block.round, 
                leaf_prev_arrivedTime=block.arrive_time,
                leaf_prev2_arrivedTime = block.arrive_time)

                sqldb.writeChainLeaf(new_leaf,block)
                sqldb.setLogBlock(block, 3)
                index = max(self.leaf) + 1
                print("lenght")
                print(index)

                self.leaf[index].append(new_leaf)
                print("max id leaf")
                print(max(self.leaf))
                
                return index

            elif(self.leaf[pos][0].leaf_hash == block.prev_hash):
                print("Sync on addBlockLeaf")
                print(block.index)
                print(block.round)
                if(self.indexMainChain < block.index):
                    #print("indexMainChain < block.index")
                    #print("Next Block")
                    #print("last hash on leaf")
                    #print(self.leaf[pos][0].leaf_hash)
                    #print("Block prev hash")
                    #print(block.prev_hash)

                    self.UpdateMainChain(block)

                    self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                    self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                    self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                    self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                    self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                    self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                    self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                    self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried

                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time
                    self.leaf[pos][0].leaf_node = block.node

                    return self.leaf[pos][0] 

                #late block
                elif(self.indexMainChain >= block.index):
                    status, round = sqldb.verifyRoundBlock(block.index, block.round)
                    if(status):
                        if(round > block.round):
                            #print("indexMainChain > block.index")
                            #print("block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index")
                            #print("Next Block")
                            #print("last hash on leaf")
                            #print(self.leaf[pos][0].leaf_hash)
                            #print("Block prev hash")
                            #print(block.prev_hash)

                            self.UpdateMainChain(block)     

                            self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                            self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                            self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                            self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                            self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                            self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                            self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                            self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 
                                    
                            self.leaf[pos][0].leaf_round = block.round
                            self.leaf[pos][0].leaf_hash = block.hash
                            self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                            self.leaf[pos][0].leaf_index = block.index
                            self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                            self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time
                            self.leaf[pos][0].leaf_node = block.node

                            self.updateLeaf(block)
                            #print("block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index")
                            #print(self.leaf)
                            return self.leaf[pos][0]

                        elif(round == block.round):

                            self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                            self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                            self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime
                            self.leaf[pos][0].leaf_prev2LastTimeTried = self.leaf[pos][0].leaf_prevLastTimeTried

                            self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                            self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                            self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime
                            self.leaf[pos][0].leaf_prevLastTimeTried = self.leaf[pos][0].leaf_lastTimeTried 

                            self.leaf[pos][0].leaf_round = block.round
                            self.leaf[pos][0].leaf_hash = block.hash
                            self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                            self.leaf[pos][0].leaf_index = block.index
                            self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                            self.leaf[pos][0].leaf_lastTimeTried = block.arrive_time

                            self.leaf[pos][0].leaf_node = block.node
                            return self.leaf[pos][0]

                        else:
                            return None
                                
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    def UpdateMainChain(self,block):
        prev_block = None
        #while not prev_block:
        prev_block = sqldb.dbtoBlock(sqldb.blockHashQuery(block.prev_hash))
        
        self.indexMainChain = block.index
        self.roundMainChain = block.round
        self.hashMainChain = block.hash
        print("CHANGE MAIN CHAIN")
        print("indexMainChain")
        print(self.indexMainChain)
     
        #print("prev_block hash")
        #print(prev_block.hash)
        #print("prevIndexMainChain")
        #print(prev_block.index)
        if(prev_block):
            self.prevIndexMainChain = prev_block.index
            print("previndexMainChain")
            print(self.prevIndexMainChain)
            self.prevRoundMainChain = prev_block.round
            self.prevHashMainChain = prev_block.hash
        else:
            self.prevIndexMainChain = block.index
            print("previndexMainChain")
            print(self.prevIndexMainChain)
            self.prevRoundMainChain = block.round
            self.prevHashMainChain = block.hash

        self.lastArrivedTime = block.arrive_time

            #verifying if the insertion change the main chain


        #if(self.leaf[pos][0].last_block_hash == block.prev_hash):
        #    new_leaf = Leaf(node=block.node, index=block.index, prev_hash=self.leaf[pos][0].prev_hash,
        #    prev2_hash=self.leaf[pos][0].prev2_hash, hash=block.hash, prev_head=self.leaf[pos][0].head,
        #    head=block.hash, round=block.round, prev_round=self.leaf[pos][0].prev_round,
        #    prev2_round=self.leaf[pos][0].prev2_round, arrivedTime=block.arrive_time,
        #    prev_arrivedTime=self.leaf[pos][0].prev_arrivedTime, prev2_arrivedTime=self.leaf[pos][0].prev2_arrivedTime)

        #if(self.leaf[pos][0].prev2_hash == block.prev_hash):
        #    new_leaf = Leaf(node=block.node, index=block.index, prev_hash=self.leaf[pos][0].prev2_hash,
        #    prev2_hash=self.leaf[pos][0].prev2_hash, hash=block.hash, prev_head=self.leaf[pos][0].head,
        #    head=block.hash, round=block.round, prev_round=self.leaf[pos][0].prev2_round,
        #    prev2_round=self.leaf[pos][0].prev2_round, arrivedTime=block.arrive_time,
        #    prev_arrivedTime=self.leaf[pos][0].prev2_arrivedTime,prev2_arrivedTime=self.leaf[pos][0].prev2_arrivedTime)
        #l = len(self.leaf)
        #l.append(new_leaf)
        #return new_leaf

        