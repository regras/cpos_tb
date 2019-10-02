import datetime
import hashlib
import random
import json


class Leaf:
    def __init__(self, leaf_index, leaf_prev_hash, leaf_round, leaf_node, leaf_arrivedTime=0, leaf_bhash=None,
    leaf_head=None, leaf_prev_head=None,leaf_prev_round=None, leaf_prev_arrivedTime=None, leaf_prev2_hash=None,
    leaf_prev2_round=None, leaf_prev2_arrivedTime=None):
        self.leaf_index = leaf_index
        self.leaf_head = leaf_head
        self.leaf_prev_head = leaf_prev_head
        self.leaf_round = leaf_round
        self.leaf_arrivedTime = leaf_arrivedTime
        self.leaf_node = leaf_node
        self.leaf_prev_hash = leaf_prev_hash
        self.leaf_prev_round = leaf_prev_round
        self.leaf_prev_arrivedTime = leaf_prev_arrivedTime
        self.leaf_prev2_hash = leaf_prev2_hash
        self.leaf_prev2_round = leaf_prev2_round
        self.leaf_prev2_arrivedTime = leaf_prev2_arrivedTime
        if leaf_bhash:
            self.leaf_hash = leaf_bhash
        else: # mostly genesis leaf
            self.leaf_hash = self.calcLeafhash()
            self.leaf_prev_hash = self.leaf_hash
            self.leaf_prev2_hash = self.leaf_hash
            self.leaf_head = self.leaf_hash
            self.leaf_prev_head = self.leaf_hash
            self.leaf_prev_round = leaf_round
            self.leaf_prev_arrivedTime = self.leaf_arrivedTime
            self.leaf_prev2_round = leaf_round
            self.leaf_prev2_arrivedTime = self.leaf_arrivedTime

            
    def calcLeafhash(self):
        
        # Check concatenate order
        h = str(self.leaf_prev_hash) + str(self.leaf_round) + str(self.leaf_node)
        return hashlib.sha256(h).hexdigest()

    #def rawleafInfo(self):
    #    return {'node': self.node, 'index': self.index , 'hash': self.hash, 'prev_hash': self.prev_hash,
    #    'prev2_hash':self.prev2_hash, 'round':self.round,'prev_round':self.prev_round,'prev2_round':self.prev2_round,
    #    'arrivedTime': self.arrivedTime,'prev_arrivedTime': self.prev_arrivedTime,'prev2_arrivedTime': self.prev2_arrivedTime}
    
    #def leafInfo(self):
    #    return json.dumps(self.rawleafInfo(), indent=4)   
