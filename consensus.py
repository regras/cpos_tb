import block
import random
import hashlib
import threading
import blockchain
import sqldb
import time
import math
import datetime
import parameter
import pickle
from collections import defaultdict

MSG_LASTBLOCK = 'getlastblock'
MSG_BLOCK = 'block'
MSG_BLOCKS = 'getblocks'
MSG_HELLO = 'hello'
MSG_PEERS = 'peers'
MSG_LEAVES = 'leaves'
MSG_BLOCKCHAIN = 'blockchain'
MSG_UNKNOWBLOCKCHAIN = 'unknowblocks'
MSG_ALLCHAIN = 'allchain'
MSG_REQBLOCK = 'reqblock'
MSG_REQBLOCKS = 'reqblocks'
MSG_REQPEER = 'reqpeers'
MSG_TX = 'transaction'



def handleMessages(bc, messages, node=None):
    cmd = messages[0] if isinstance(messages, list) else str(messages)
    cmd = cmd.lower()
    if cmd == MSG_LASTBLOCK:
        return bc.getLastBlock()
    elif cmd == MSG_HELLO:
        return MSG_HELLO
    elif cmd == MSG_BLOCKS:
        return sqldb.blocksQuery(messages)
    elif cmd == MSG_BLOCK:
        return sqldb.blockQuery(messages)
    elif cmd == MSG_LEAVES:
        return sqldb.dbCheckLeaf(bc)
    elif cmd == MSG_BLOCKCHAIN:
        return sqldb.dbCheckChain([messages[1], messages[2]])
    elif cmd == MSG_REQBLOCKS:
        return sqldb.dbReqBlocks([messages[1], messages[2], messages[3]])
    elif cmd == MSG_ALLCHAIN:
        return sqldb.dbGetAllChain([messages[1]])
    elif cmd == MSG_REQBLOCK:
        return sqldb.dbReqBlock([messages[1],messages[2]])
    elif cmd == MSG_REQPEER:
        salt = messages[1]
        ipaddr = messages[2]
        peerSalt = str(node.getIp()) + str(salt)
        distance = int(hashlib.sha256(str(ipaddr)).hexdigest(),16) ^ int(hashlib.sha256(peerSalt).hexdigest(),16)
        if(distance <= parameter.theta * float((2**256 - 1))):
            if(node.getNumAccepted() < parameter.k):
                localSalt = node.getLocalSalt()
                peerSalt = str(ipaddr) + str(localSalt)
                localDistance = int(hashlib.sha256(str(node.getIp())).hexdigest(),16) ^ int(hashlib.sha256(peerSalt).hexdigest(),16)                
                node.insertAcceptPeer(ipaddr,localDistance)
                return True
            else:
                localSalt = node.getLocalSalt()
                peerSalt = str(ipaddr) + str(localSalt)
                localDistance = int(hashlib.sha256(str(node.getIp())).hexdigest(),16) ^ int(hashlib.sha256(peerSalt).hexdigest(),16)
                if(node.checkDistance(ipaddr,localDistance)):
                    node.insertAcceptPeer(ipaddr,localDistance)
                    return True
        return False
    else:
        return None


class Consensus:

    def __init__(self):
        self.type = "PoS"
        
        #i = 1
        #exp = 255
        self.target = (2**(256 - parameter.difficulty))
        #while i <= parameter.difficulty:
        #    self.target = self.target - (2**(exp))
        #    i = i + 1
        #    exp = exp - 1
        print("consensus")
        print('result of consensus target {}'.format(self.target))
            
    def getTarget(self):
        return self.target
        
    def POS(self, lastBlock_hash, round, node, skip = None, tx=0):
        """ Find nonce for PoW returning block information """
        # chr simplifies merkle root and add randomness
        #tx = chr(random.randint(1,100))

        user_header = str(round) + str(node) # user header
        user_hash = hashlib.sha256(user_header).hexdigest()

        block_header = str(lastBlock_hash) + str(tx)
        block_hash = hashlib.sha256(block_header).hexdigest()

        return user_hash, block_hash
        
    def calcProofHash(self,userHash,blockHash,subUser):
        j = 1
        header = str(userHash) + str(j)
        proofHash = hashlib.sha256(header).hexdigest()
        while(j < subUser):
            j = j + 1
            header = str(userHash) + str(j)
            newHash = hashlib.sha256(header).hexdigest()
            if(int(proofHash,16) > int(newHash,16)):
                proofHash = newHash
        return proofHash, j
        #print(hash_result)
        #print(format(int(hash_result, 16),"0256b"))
        #print(format(self.target,"0256b"))

        #if int(hash_result,16) < self.target:
            # print("OK")
        #    return hash_result, tx

        #return False, tx

    #def generateNewblock(self, lastBlock, node, stake, skip=False):
    #    """ Loop for PoS in case of solve challenge, returning new Block object """
    #    r = int(math.floor((int(time.mktime(datetime.datetime.now().timetuple())) - int(lastBlock.arrive_time)) / int(parameter.timeout))) + 1

        #while True and not skip.is_set():
    #    while True :

    #	    round = lastBlock.round + r
    #        new_hash, tx = self.POS(lastBlock, round, node, stake, skip)
    #        if not tx:
    #            return None

    #        print('new block' if new_hash else 'try again!')

    #        if new_hash:
    #            arrive_time = int(time.mktime(datetime.datetime.now().timetuple()))
    #            return block.Block(lastBlock.index + 1, lastBlock.hash, round, node, arrive_time, new_hash, tx)

    #        time.sleep(parameter.timeout)
    #        r = r + 1
            # print(r)

        return None

    def rawConsensusInfo(self):
        return {'difficulty': parameter.difficulty, 'type': self.type}
