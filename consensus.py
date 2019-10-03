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

MSG_LASTBLOCK = 'getlastblock'
MSG_BLOCK = 'block'
MSG_BLOCKS = 'getblocks'
MSG_HELLO = 'hello'
MSG_PEERS = 'peers'
MSG_LEAVES = 'leaves'
MSG_BLOCKCHAIN = 'blockchain'
MSG_UNKNOWBLOCKCHAIN = 'unknowblocks'
MSG_ALLCHAIN = 'allchain'

def handleMessages(bc, messages):
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
    elif cmd == MSG_UNKNOWBLOCKCHAIN:
        return sqldb.dbCheckUnknowChain([messages[1]])
    elif cmd == MSG_ALLCHAIN:
        return sqldb.dbGetAllChain([messages[1]])
    else:
        return None


class Consensus:

    def __init__(self):
        self.type = "PoS"
        self.target = 2**(256 - parameter.difficulty) - 1

    def POS(self, lastBlock_hash, round, node, stake, skip = None):
        """ Find nonce for PoW returning block information """
        # chr simplifies merkle root and add randomness
        tx = chr(random.randint(1,100))

        c_header = str(lastBlock_hash) + str(round) + str(node) # candidate header

        hash_result = hashlib.sha256(c_header).hexdigest()
        #print(hash_result)
        #print(format(int(hash_result, 16),"0256b"))
        #print(format(self.target,"0256b"))

        if int(hash_result,16) < self.target:
            # print("OK")
            return hash_result, tx

        return False, tx

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
