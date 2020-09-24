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

    if len(sys.argv) >= 2:
        try:
            if(MSG_MONITOR == sys.argv[1]):
                ctx = zmq.Context.instance()
                reqsocket = ctx.socket(zmq.REQ)
                reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                print("produce transaction node: ", sys.argv[2])

                reqsocket.send_multipart([MSG_FMINE, str(0)])
                print(reqsocket.recv_string())

                reqsocket.send(MSG_CONNECT)
                print(reqsocket.recv_string())
            
            elif(MSG_STARTPEER == sys.argv[1]):
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

                        #time.sleep(2)
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
            elif(MSG_TRANS == sys.argv[1]):
                peers = parameter.peers
                numtrans = 0
                i = 0
                while (i < len(peers)):
                    try:                         
                        ctx = zmq.Context.instance()
                        reqsocket = ctx.socket(zmq.REQ)
                        reqsocket.setsockopt(zmq.RCVTIMEO, 5000)    
                        reqsocket.connect("tcp://%s:9999" % peers[i])
                        print("Transmission for node : ", peers[i])
                        reqsocket.send_multipart([MSG_TRANS,sys.argv[2]])
                        reply = reqsocket.recv_pyobj()
                        if(reply[0]):
                            numtrans = numtrans + reply[0]
                    except Exception as e:
                            print(str(e))
                    i = i + 1
                print("total transmission: %d" %numtrans)    
            elif(MSG_EXPLORER == sys.argv[1]):
                avgconf = 0
                callsync = 0
                callsyncrev = 0
                numrevblock = 0
                receivedblocks = 0
                numround = 0
                numblockstable = 0
                lateblocks = 0
                numblocks = 0
                if(len(sys.argv) == 3):
                    peers = parameter.peers
                    i = 0               
                    while (i < len(peers)):
                        try:
                            ctx = zmq.Context.instance()
                            reqsocket = ctx.socket(zmq.REQ)
                            reqsocket.setsockopt(zmq.RCVTIMEO, 5000)    
                            reqsocket.connect("tcp://%s:9999" % peers[i])
                            print("Explorer node : ", peers[i])
                            reqsocket.send_multipart([MSG_EXPLORER, sys.argv[2]])

                            reply = reqsocket.recv_pyobj()
                            avgconf = avgconf + reply[0]
                            callsync = callsync + reply[1]
                            callsyncrev = callsyncrev + reply[2]
                            numrevblock = numrevblock + reply[3]
                            receivedblocks = receivedblocks + reply[4]
                            numround = int(reply[5])
                            numblockstable = int(reply[6])
                            lateblocks = lateblocks + int(reply[7])
                            numblocks = int(reply[8])
                        except Exception as e:
                            print(str(e))
                        i = i + 1
                    if(len(peers) > 0):
                        avgconf = avgconf / float(len(peers))
                        print("block confirmation average in the network view (block/round): %f \n" % avgconf)
                    print("Confirmation Blocks number: %d\n" %numblockstable)
                    print("produced blocks: %d \n" %numblocks)
                    print("sync function calls number in the network view: %d \n" % callsync)
                    print("Reversions number in the network view: %d \n" % callsyncrev)
                    print("Reversed blocks number in the network view: %d \n" % numrevblock)
                    if(callsyncrev > 0):
                        print("Reversed blocks number average in the network view (Reversed blocks number / revertion): %f \n" % (float(numrevblock) / callsyncrev))
                    print("Received blocks number: %d \n" % receivedblocks)
                    print("Round number: %d \n" % numround)
                    print("late blocks number: %d \n" % lateblocks)

                elif(len(sys.argv) > 3):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                    print("Explorer node : ", sys.argv[2])
                    reqsocket.send_multipart([MSG_EXPLORER, sys.argv[3]])
                    reply = reqsocket.recv_pyobj()

                    avgconf = reply[0]
                    callsync = reply[1]
                    callsyncrev = reply[2]
                    numrevblock = reply[3]
                    receivedblocks = reply[4]
                    numround = reply[5]
                    numblockstable = int(reply[6])
                    lateblocks = int(reply[7])
                    numblocks = int(reply[8])
                    
                    print("Block confirmation average (block/round): %f \n" % avgconf)
                    print("Confirmation Blocks number: %d" %numblockstable)
                    print("produced blocks: %d \n" %numblocks)
                    print("Sync function calls number: %d \n" % callsync)
                    print("Reversions number: %d \n" % callsyncrev)
                    print("Reversed blocks number: %d \n" % numrevblock)
                    if(callsyncrev > 0):
                        print("Reversed blocks number average (Reversed blocks number / revertion): %f \n" % (float(numrevblock) / callsyncrev))
                    print("Received blocks number : %d \n" % receivedblocks)
                    print("Round number: %d \n" % numround)                                                            
                    print("late blocks number: %d \n" % lateblocks)
                else:
                    print("eplorer command failed")

            elif(MSG_STOP == sys.argv[1]):
                if(len(sys.argv) == 2):
                    peers = parameter.peers
                    i = 0
                    while(i < len(peers)):
                        ctx = zmq.Context.instance()
                        reqsocket = ctx.socket(zmq.REQ)
                        reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                        reqsocket.connect("tcp://%s:9999" % peers[i])
                        reqsocket.send(sys.argv[1])
                        print(reqsocket.recv_string())
                        i = i + 1
                elif(len(sys.argv) > 2):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                    reqsocket.send(sys.argv[1])
                    print(reqsocket.recv_string())
                    
                else:
                    print("stopping command failed")
              
            elif(MSG_SHOWPEERS == sys.argv[1]):
                ctx = zmq.Context.instance()
                reqsocket = ctx.socket(zmq.REQ)
                reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                reqsocket.connect("tcp://%s:9999" % sys.argv[2])                
                reqsocket.send(sys.argv[1])
                peers = reqsocket.recv_pyobj()
                print("Node Peers: \n")
                for i in peers:
                    print(i)
                    print("\n")
            else:
                print("Unknown command")            

        except zmq.Again:
            print("Command failed")
        sys.exit(0)
        reqsocket.close(linger=0)
        ctx.term()


    sys.exit(0)