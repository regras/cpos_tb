from block import Block
from collections import deque
import json
import time
import datetime
import parameter


class Blockchain:
    def __init__(self, db=None):
        self.chain = deque()
        if db:
            # order in database definition
            b = (
                db
                if isinstance(db, Block)
                else Block(
                    index=db[0],
                    round=db[1],
                    prev_hash=db[2],
                    b_hash=db[3],
                    arrive_time=db[7],
                    node=db[4],
                    tx=db[6],
                )
            )
            self.chain.appendleft(b)
        else:
            genesisBlock = Block(0, "", 1, "", parameter.GEN_ARRIVE_TIME)
            self.chain.appendleft(genesisBlock)

    def getchain(self):
        return self.chain

    def getLastBlock(self):
        return self.chain[0]

    def rawBlockchainInfo(self):
        return {"chain lenght": len(self.chain)}

    def Info(self):
        blocks = []
        for i in reversed(self.chain):
            blocks.append(i.rawblockInfo())
        return json.dumps({"blocks": blocks}, indent=4)

    def addBlocktoBlockchain(self, Block):
        self.chain.appendleft(Block)

    def serializeblockchain(self):
        with open("blockchain.json", "w") as write_file:
            json.dump(self.Info, write_file)
