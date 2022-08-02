import datetime
import hashlib
import random
import json


class Block:
    def __init__(
        self,
        index,
        prev_hash,
        round,
        node,
        arrive_time=0,
        b_hash=None,
        tx="",
        subuser=1,
        proof_hash=0,
        create_time=0,
    ):
        self.index = index
        self.prev_hash = prev_hash
        self.tx = tx
        self.round = round
        self.node = node
        self.mroot = self.calcMerkleRoot()
        self.arrive_time = arrive_time
        self.create_time = create_time
        self.subuser = subuser
        if proof_hash:
            self.proof_hash = proof_hash
        else:
            self.proof_hash = self.calcProofHash()

        if b_hash:
            self.hash = b_hash
        else:  # mostly genesis
            self.hash = self.calcBlockhash()

    def calcMerkleRoot(self):
        return hashlib.sha256(self.tx).hexdigest()

    def calcProofHash(self):
        user_header = str(self.round) + str(self.node)  # user header
        user_hash = hashlib.sha256(user_header).hexdigest()

        c_header = str(user_hash) + str(self.subuser)
        return hashlib.sha256(c_header).hexdigest()

    def calcBlockhash(self):
        # Check concatenate order
        h = str(self.prev_hash) + str(self.tx)
        h = hashlib.sha256(h).hexdigest()
        h = str(h) + str(self.proof_hash)
        return hashlib.sha256(h).hexdigest()

    def rawblockInfo(self):
        return {
            "index": self.index,
            "round": self.round,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "node": self.node,
            "merkle_root": self.mroot,
            "tx": self.tx,
            "arrive_time": self.arrive_time,
        }

    def blockInfo(self):
        return json.dumps(self.rawblockInfo(), indent=4)
