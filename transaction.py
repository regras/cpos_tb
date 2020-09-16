#!/usr/bin/env python
import sqldb
import threading
import time
import parameter
from random import randint
import pickle
import zmq
import consensus
class StopException(Exception):
    pass

class Transaction(object): 
    
    """ Transaction class """
    def __init__(self,node_ipaddr = '127.0.0.1', port = 9000):
        self.ctx = zmq.Context.instance()
        self.poller = zmq.Poller()
        self.router = self.ctx.socket(zmq.REQ)
        self.poller.register(self.router, zmq.POLLIN)
        self.port = port
        self.node_ipaddr = node_ipaddr
    
    def sendtx(self, tx, address):
        m = None
        if address:
            self.router.connect("tcp://%s:%s" %(address, self.port+1))
            #print("IP")
            #print(address)
            time.sleep(2)
            try:
                self.router.send_multipart([consensus.MSG_TX,tx])
                m = self._poll(self.router)[0]
            except Exception as e:
                print(str(e))

            self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        return m

    def startGenTransaction(self):
        peers = parameter.peers
        txtime = float(parameter.txround) / parameter.timeout             
        while True:
            apeer = peers[randint(1,len(peers)-1)]
            tx = sqldb.createtx(self.node_ipaddr)
            tx = pickle.dumps(tx,2)
            if(tx):
                self.sendtx(tx,apeer) 
            time.sleep(txtime)

def main():
    tx = Transaction()
    tx_thread = threading.Thread(name='tx_thread',target=tx.startGenTransaction)
    tx_thread.start()
    
if __name__ == '__main__':
    main()'''
        