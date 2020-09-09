#!/usr/bin/env python

import zmq
import sys
from messages import *
import parameter
import hashlib
import time

if __name__ == '__main__':
    help_string = '''usage: %s [-h]
        <command> [<args>]

Blockchain RPC client

These are the commands available:

getlastblock        Print the last block info
getblock <index>    Print the block info with index <index>
getblocks <list>    Print the blocks info from index <list>
startmining         Start the miner thread
stopmining          Stop the miner thread
addbalance <quantity> Add <quantity> of coins
addblock <list>     Add block manually from <list> [index, round]
addpeer <ip>        Add <ip> to the node peers list
removepeer <ip>     Remove <ip> to the node peers list
getpeerinfo         Print the peers list
exit                Terminate and exit the node.py program running
''' 
    stake = parameter.numStake
    peers = parameter.peers
    i = 0
    while(i < len(peers)):
        ctx = zmq.Context.instance()
        reqsocket = ctx.socket(zmq.REQ)
        reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
        print(peers[i])
        reqsocket.connect("tcp://%s:9999" % peers[i])    
        try:
            #peer connect
            reqsocket.send(MSG_CONNECT)
            print(reqsocket.recv_string())

            time.sleep(2)
            #stake node
            h = hashlib.sha256(str(peers[i])).hexdigest()            
            s = stake[1][h][0]            
            reqsocket.send_multipart([MSG_STAKE, str(s)])
            print(reqsocket.recv_string())
            
        except zmq.Again:
            print("Command failed")
        
        reqsocket.close(linger=0)
        ctx.term()
        i = i + 1

    #starting mining process
    '''i = 0
    while(i < len(peers)):
        time.sleep(1)
        ctx = zmq.Context.instance()
        reqsocket = ctx.socket(zmq.REQ)
        reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
        print(peers[i])
        reqsocket.connect("tcp://%s:9999" % peers[i])    
        try:
            reqsocket.send(MSG_START)
            print(reqsocket.recv_string())
        except zmq.Again:
            print("command failed")
        reqsocket.close(linger=0)
        ctx.term()
        i = i + 1'''
    sys.exit(0)