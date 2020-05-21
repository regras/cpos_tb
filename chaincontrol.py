from collections import defaultdict
import json
import time
import datetime
import parameter
import sqldb
import threading

'''def removeLeaf(self,pos):
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
        print("chain not removed with success. Fork point not found.")'''

def updateChainView(idChain, block):
    if(sqldb.blockIsMaxIndex(block.index)):
        sqldb.writeChainLeaf(idChain, block)
        return True

    elif((not sqldb.blockIsMaxIndex(block.index)) and (sqldb.blockIsLeaf(block.index,block.prev_hash))):
        if(sqldb.verifyRoundBlock(block.index,block.round)):
            print("ISLEAF")
            print("NOT MAXINDEX")
            sqldb.removeAllBlocksHigh(block.index, block.hash)
            sqldb.writeChainLeaf(idChain, block)
            return True
        else:
            return False

    elif(not sqldb.blockIsLeaf(block.index, block.prev_hash)):
        if(sqldb.verifyRoundBlock(block.index,block.round)):
            status = sqldb.removeAllBlocksHigh(block.index, block.hash)
            if(status):
                sqldb.writeChainLeaf(idChain, block)
            else:
                print("NEW FORK")
                sqldb.createNewChain(block)
                sqldb.setForkFromBlock(block.prev_hash)
            return True
        else:
            return False
        
    else:
        print("not insert new block")
        return False
            
def addBlockLeaf(block=None, sync=False):
    #inserting block on the chain's top
    if(not sync):
        idChain = sqldb.getIdChain(block.prev_hash)
        if(idChain):
            status = updateChainView(idChain, block)
            if(status):
                return True,True
            else:
                return True,False
        else:
            return False,False
        
