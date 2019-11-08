from leaf import Leaf
from collections import defaultdict
import json
import time
import datetime
import parameter
import sqldb
class Leafchain:
    def __init__(self, db=None):

        self.indexMainChain = 0
        self.roundMainChain = 0
        self.hashMainChain = 0
        self.prevIndexMainChain = 0
        self.prevRoundMainChain = 0
        self.prevHashMainChain = 0
        self.lastArrivedTime = parameter.GEN_ARRIVE_TIME
        self.leaf = defaultdict(list)

        if db:
            # order in database definition
            l = db if isinstance(db, Leaf) else Leaf(leaf_node=db[4],leaf_index=db[0],leaf_head=db[8],leaf_prev_head=db[9],
            leaf_bhash=db[3], leaf_round=db[1],leaf_arrivedTime=db[7],leaf_prev_hash=db[10],leaf_prev_round=db[11],
            leaf_prev_arrivedTime=db[12],leaf_prev2_hash=db[13],leaf_prev2_round=db[14],
            leaf_prev2_arrivedTime=db[15])
            self.leaf[0].append(l)

            block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',l.leaf_hash]))
            self.UpdateMainChain(block)    
            
        else:
            l = Leaf(0,"",1,"",parameter.GEN_ARRIVE_TIME)
            self.leaf[0].append(l)

            self.indexMainChain = 0
            self.roundMainChain = 1
            self.hashMainChain = l.leaf_hash
            self.prevIndexMainChain = 0
            self.prevRoundMainChain = 1
            self.prevHashMainChain = l.leaf_hash

       
    def setLastArrivedTime(self,arrive_time):
        self.lastArrivedTime = arrive_time

            
    def getLenLeaf(self):
        return (len(self.leaf)) 

    def getLeafs(self):
        return self.leaf

    def getLastArrivedTime(self):
        return self.lastArrivedTime
    
    def getRoundMainChain(self):
        return self.roundMainChain
    
    def getIndexMainChain(self):
        return self.indexMainChain
    
    #def getElementByPosition(self,pos):
    #    if(pos < self.getLenLeaf()):
    #        return self.leaf[pos][0] 
    
    def getMainChain(self):
            return self.roundMainChain, self.indexMainChain, self.prevRoundMainChain, self.prevIndexMainChain

    def appendLeaf(self,db):
        l = db if isinstance(db, Leaf) else Leaf(leaf_node=db[4],leaf_index=db[0],leaf_head=db[8],leaf_prev_head=db[9],
        leaf_bhash=db[3], leaf_round=db[1],leaf_arrivedTime=db[7],leaf_prev_hash=db[10],leaf_prev_round=db[11],
        leaf_prev_arrivedTime=db[12],leaf_prev2_hash=db[13],leaf_prev2_round=db[14],
        leaf_prev2_arrivedTime=db[15])
        self.leaf[max(self.leaf)+1].append(l)
        if(l.leaf_index > self.indexMainChain):
            block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',l.leaf_hash]))
            self.UpdateMainChain(block)    
    
    def removeLeaf(self,pos):
        print("remove chain with head")
        print(self.leaf[pos][0].leaf_head)
        #sqldb.setLogFork(self.leaf[pos][0].leaf_head,'0')
        sqldb.setLogFork(self.leaf[pos][0].leaf_head, self.leaf[pos][0].leaf_arrivedTime, 0, 0, self.leaf[pos][0].leaf_index)
        sqldb.removeLeafChain(['',self.leaf[pos][0].leaf_head])
        del self.leaf[pos]
        
    
    def IsLeaf(self, block_hash):
        for k, l in self.leaf.iteritems():
            if(block_hash == l[0].leaf_hash):
                return True
        return False
        
    def updateLeaf(self, block):
        for k,l in list(self.leaf.iteritems()):
        
            if(self.leaf[k][0].leaf_round > block.round):
                prev_block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',self.leaf[k][0].leaf_prev_hash]))
                sqldb.removeBlock(['',self.leaf[k][0].leaf_hash])
                if(not self.IsLeaf(prev_block.hash) and (prev_block.hash != block.prev_hash)):

                    new_prev2_block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',prev_block.prev_hash]))
                    if(new_prev2_block):
                        self.leaf[k][0].leaf_prev2_round = new_prev2_block.round
                        self.leaf[k][0].leaf_prev2_hash = new_prev2_block.hash
                        self.leaf[k][0].leaf_prev2_arrivedTime = new_prev2_block.arrive_time

                        self.leaf[k][0].leaf_prev_round = self.leaf[k][0].leaf_prev2_round 
                        self.leaf[k][0].leaf_prev_hash = self.leaf[k][0].leaf_prev2_hash
                        self.leaf[k][0].leaf_prev_arrivedTime = self.leaf[k][0].leaf_prev2_arrivedTime

                        self.leaf[k][0].leaf_round = prev_block.round
                        self.leaf[k][0].leaf_hash = prev_block.hash
                        self.leaf[k][0].leaf_prev_hash = prev_block.prev_hash
                        self.leaf[k][0].leaf_index = prev_block.index
                        self.leaf[k][0].leaf_arrivedTime = prev_block.arrive_time
                else:
                    del self.leaf[k]
        #print (self.leaf)        
       
    def addBlockLeaf(self,pos, block, sync=False):
        #inserting block on the chain's top
        if(self.leaf[pos][0].leaf_hash == block.prev_hash and not sync):
            if(self.indexMainChain < block.index):

                self.UpdateMainChain(block)

                self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime

                self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime

                self.leaf[pos][0].leaf_round = block.round
                self.leaf[pos][0].leaf_hash = block.hash
                self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

                self.leaf[pos][0].leaf_index = block.index

                return self.leaf[pos][0] 

            #late block
            if(self.indexMainChain > block.index):
                if(block.round < self.prevRoundMainChain and self.prevIndexMainChain == block.index):
                    self.UpdateMainChain(block)               
                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                    self.UpdateLeaf(block)

                if(block.round == self.prevRoundMainChain and self.prevIndexMainChain == block.index):

                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

            if(self.indexMainChain == block.index):

                if(block.round == self.roundMainChain):
                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

                if(block.round < self.roundMainChain):
                    self.UpdateMainChain(block)               
                    self.leaf[pos][0].leaf_round = block.round
                    self.leaf[pos][0].leaf_hash = block.hash
                    self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                    self.leaf[pos][0].leaf_index = block.index
                    self.leaf[pos][0].leaf_arrivedTime = block.arrive_time
                    self.updateLeaf(block)

        elif(self.leaf[pos][0].leaf_prev_hash == block.prev_hash and not sync):
            print("POSSIVEL NOVO FORK")
            
            if (block.round > self.roundMainChain):
                print("Round Maior")
                return self.leaf[pos][0]
            
            elif(block.round < self.roundMainChain):

                print("Round Menor")
                new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash=block.prev_hash,
                leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                leaf_prev_head=self.leaf[pos][0].leaf_prev_head, leaf_head=self.leaf[pos][0].leaf_head, leaf_round=block.round,
                leaf_prev_round=self.leaf[pos][0].leaf_prev_round,leaf_prev2_round=self.leaf[pos][0].leaf_prev2_round, 
                leaf_prev_arrivedTime=self.leaf[pos][0].leaf_prev_arrivedTime,
                leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev2_arrivedTime)

                self.leaf[max(self.leaf)+1].append(new_leaf)

                self.UpdateMainChain(block)
                self.updateLeaf(block)
                sqldb.writeChainLeaf(new_leaf,block)

                
                #sqldb.setLogFork(self.leaf[pos][0].leaf_head,'1')

            else:
                print("Round Igual")
                new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash="",
                leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                leaf_prev_head=self.leaf[pos][0].leaf_head, leaf_head=block.hash, leaf_round=block.round,
                leaf_prev_round=block.round,leaf_prev2_round=block.round, 
                leaf_prev_arrivedTime=block.arrive_time,
                leaf_prev2_arrivedTime = block.arrive_time)

                lenght = max(self.leaf) + 1
                self.leaf[lenght].append(new_leaf)

                sqldb.writeChainLeaf(new_leaf,block)

                sqldb.setForkFromBlock(self.leaf[pos][0].leaf_prev_hash)

                sqldb.setLogFork(self.leaf[lenght][0].leaf_head,self.leaf[lenght][0].leaf_arrivedTime,1,self.leaf[lenght][0].leaf_index,0,self.leaf[lenght][0].leaf_prev_head)

           
    
            #print("NOVA CHAIN")
            #print("hash na atual Leaf")
            #print(self.leaf[pos][0].head)
            #print("Head da nova Leaf")
            #print(block.hash)
            #print("prev2_arrivedTime novo")
            #print(self.leaf[pos][0].prev2_arrivedTime)

       
            return new_leaf
        elif(self.leaf[pos][0].leaf_prev2_hash == block.prev_hash and not sync):

            print("POSSIVEL NOVO FORK NO PREV2_ROUND")
            if (block.round > self.prevRoundMainChain):
                print("Round Maior")
                return self.leaf[pos][0]

            elif(block.round < self.prevRoundMainChain):
                print("Round Menor")

                new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash=block.prev_hash,
                leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                leaf_prev_head=self.leaf[pos][0].leaf_prev_head, leaf_head=self.leaf[pos][0].leaf_head, leaf_round=block.round,
                leaf_prev_round=self.leaf[pos][0].leaf_prev_round,leaf_prev2_round=block.round, 
                leaf_prev_arrivedTime=self.leaf[pos][0].leaf_prev_arrivedTime,
                leaf_prev2_arrivedTime = block.arrive_time)

                self.leaf[max(self.leaf)+1].append(new_leaf)

                self.UpdateMainChain(block)
                self.updateLeaf(block)

                sqldb.writeChainLeaf(new_leaf,block)

                
            else:
                print("Round Igual")

                new_leaf = Leaf(leaf_index=block.index,leaf_prev_hash="",
                leaf_node=block.node,leaf_arrivedTime=block.arrive_time, leaf_bhash=block.hash,
                leaf_prev_head=self.leaf[pos][0].leaf_head, leaf_head=block.hash, leaf_round=block.round,
                leaf_prev_round=block.round,leaf_prev2_round=block.round, 
                leaf_prev_arrivedTime=block.arrive_time,
                leaf_prev2_arrivedTime = block.arrive_time)

                lenght = max(self.leaf) + 1
                self.leaf[lenght].append(new_leaf)
                sqldb.writeChainLeaf(new_leaf,block)
                
                sqldb.setForkFromBlock(self.leaf[pos][0].leaf_prev_hash)
            
                sqldb.setLogFork(self.leaf[lenght][0].leaf_head,self.leaf[lenght][0].leaf_arrivedTime,1,self.leaf[lenght][0].leaf_index,0,self.leaf[lenght][0].leaf_prev_head)

            return new_leaf

        elif(sync):
                self.leaf[pos][0].leaf_prev2_round = self.leaf[pos][0].leaf_prev_round
                self.leaf[pos][0].leaf_prev2_hash = self.leaf[pos][0].leaf_prev_hash
                self.leaf[pos][0].leaf_prev2_arrivedTime = self.leaf[pos][0].leaf_prev_arrivedTime

                self.leaf[pos][0].leaf_prev_round = self.leaf[pos][0].leaf_round
                self.leaf[pos][0].leaf_prev_hash = self.leaf[pos][0].leaf_hash
                self.leaf[pos][0].leaf_prev_arrivedTime = self.leaf[pos][0].leaf_arrivedTime

                self.leaf[pos][0].leaf_round = block.round
                self.leaf[pos][0].leaf_hash = block.hash
                self.leaf[pos][0].leaf_prev_hash = block.prev_hash
                self.leaf[pos][0].leaf_arrivedTime = block.arrive_time

                self.leaf[pos][0].leaf_index = block.index

                return self.leaf[pos][0]

        return self.leaf[pos][0]    

    def UpdateMainChain(self,block):
        prev_block = None
        #while not prev_block:
        prev_block = sqldb.dbtoBlock(sqldb.blockHashQuery(['',block.prev_hash]))
        
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

        