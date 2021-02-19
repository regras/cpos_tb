#!/usr/bin/env python

import zmq
import sys
from messages import *
import parameter
import hashlib
import time
import datetime
import statistics

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
                startTime = float(time.mktime(datetime.datetime.now().timetuple()))
                while(i < len(peers)):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    print(peers[i])
                    reqsocket.connect("tcp://%s:9999" % peers[i])    
                    try:
                        #peer connect
                        reqsocket.send_multipart([MSG_CONNECT,str(startTime)])
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
                numtransBlock = 0
                listnumtransBlock = []
                numtransHeader = 0
                listnumtransHeader = []
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
                            numtransBlock = numtransBlock + reply[0]
                            listnumtransBlock = listnumtransBlock + [int(reply[0])]
                            if(reply[1]):
                                numtransHeader = numtransHeader + reply[1]
                                listnumtransHeader = listnumtransHeader + [int(reply[1])]
                    except Exception as e:
                            print(str(e))
                    i = i + 1
                avgtransBlock = float(numtransBlock) / len(listnumtransBlock)
                varianceBlock = statistics.pvariance(listnumtransBlock,avgtransBlock)
                avgtransHeader = float(numtransHeader) / len(listnumtransHeader)
                varianceHeader = statistics.pvariance(listnumtransHeader,avgtransHeader)
                #for k in listnumtrans:
                #    print(k)
                print("total block transmission: %d" %numtransBlock)
                print("avg block transmission: ", avgtransBlock)
                print("avg block variance: ", varianceBlock)

                print("total header transmission: %d" %numtransHeader)
                print("avg header transmission: ", avgtransHeader)
                print("avg header variance: ", varianceHeader)

                
            elif(MSG_EXPLORER == sys.argv[1]):
                avgconf = 0
                callsync = 0
                listcallsync = []
                callsyncrev = 0
                listcallsyncrev = []
                numrevblock = 0
                listnumrevblock = []
                receivedblocks = 0
                listreceivedblocks = []
                numround = 0
                numblockstable = 0
                listnumblockstable = []
                lateblocks = 0
                listratelateblocks = []
                ratelateblocks = 0
                listlateblocks = []                
                numblocks = 0
                listnumblocks = []
                mainchainProducedBlock = 0
                listmainchainProducedBlock = []
                allblockswithconfirmed = 0
                listallblockwithconfirmed = []
                numsuc = 0
                listnumsuc = []
                listAvgConf = []
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
                            #time.sleep(5)
                            reply = reqsocket.recv_pyobj()
                            avgconf = avgconf + reply[0]
                            listAvgConf = listAvgConf + [reply[0]]
                            callsync = callsync + reply[1]
                            listcallsync = listcallsync + [reply[1]]
                            callsyncrev = callsyncrev + reply[2]
                            listcallsyncrev = listcallsyncrev + [reply[2]]
                            numrevblock = numrevblock + reply[3]
                            listnumrevblock = listnumrevblock + [reply[3]]
                            receivedblocks = receivedblocks + reply[4]
                            listreceivedblocks = listreceivedblocks + [reply[4]]
                            numround = int(reply[5])
                            numblockstable = numblockstable + int(reply[6])
                            listnumblockstable = listnumblockstable + [int(reply[6])]
                            print("confirmed block by node %s : %d" %(peers[i],int(reply[6])))
                            lateblocks = lateblocks + int(reply[7])
                            listlateblocks = listlateblocks + [int(reply[7])]
                            if(reply[4] > 0):
                                ratelateblocks = ratelateblocks + float(reply[7]) / reply[4]
                                listratelateblocks = listratelateblocks + [float(reply[7])/reply[4]]
                            numblocks = numblocks + int(reply[8])
                            listnumblocks = listnumblocks + [int(reply[8])]
                            numsuc = numsuc + int(reply[9])
                            listnumsuc = listnumsuc + [int(reply[9])]
                            mainchainProducedBlock = mainchainProducedBlock + int(reply[10])
                            listmainchainProducedBlock = listmainchainProducedBlock + [int(reply[10])]
                            allblockswithconfirmed = allblockswithconfirmed + int(reply[11])
                            listallblockwithconfirmed = listallblockwithconfirmed + [int(reply[11])]
                            print("produced block in main chain by node %s: %d" %(peers[i],int(reply[10])))
                            print("all produced block with a confirmed block: %d" %(reply[11]))
                        except Exception as e:
                            print(str(e))
                        i = i + 1

                    #########sync calls###############
                    print("sync function calls number in the network view: %d" % callsync)
                    if(callsync > 0):
                        avg = callsync / float(len(listcallsync))
                        variance = statistics.pvariance(listcallsync, avg)
                        print("average of the sync function calls:", avg)
                        print("variance of the sync function calls:", variance)
                    print("\n")

                    #########reversions number########
                    print("Reversions number in the network view: %d \n" % callsyncrev)
                    if(callsyncrev > 0):
                        avg = callsyncrev / float(len(listcallsyncrev))
                        variance = statistics.pvariance(listcallsyncrev, avg)
                        print("average of the reversions number: ", avg)
                        print("variance of the reversions number:", variance)
                    print("\n")

                    #########reversed blocks number#######
                    print("Reversed blocks number in the network view: %d \n" % numrevblock)
                    if(numrevblock > 0):
                        avg = numrevblock / float(len(listnumrevblock))
                        variance = statistics.pvariance(listnumrevblock,avg)
                        print("average of reversed blocks number: ", avg)
                        print("variance of the reversed blocks number: ", variance)
                    print("\n")

                    #########received blocks number######
                    print("Received blocks number: %d \n" % receivedblocks)
                    if(receivedblocks > 0):
                        avg = receivedblocks / float(len(listreceivedblocks))
                        variance = statistics.pvariance(listreceivedblocks, avg)
                        print("average of the received blocks number: ", avg)
                        print("variance of the received blocks number: ", variance)
                    print("\n")

                    ##########late blocks number########
                    print("late blocks number: %d \n" % lateblocks)
                    if(lateblocks > 0):
                        avg = lateblocks / float(len(listlateblocks))
                        variance = statistics.pvariance(listlateblocks, avg)
                        print("average of the last blocks number: ", avg)
                        print("variance of the last blocks number: ", variance)
                        if(ratelateblocks > 0):
                            avg = ratelateblocks / float(len(listratelateblocks))
                            variance = statistics.pvariance(listratelateblocks, avg)
                            print("average of the rate late blocks: ", avg)
                            print("variance of the rate late blocks: ", variance)
                    print("\n")

                    if(avgconf > 0):
                        avg = avgconf / float(len(listAvgConf))
                        print("block confirmation average in the network view (block/round): %f \n" % avg)
                        variance = statistics.pvariance(listAvgConf,avg)
                        print("variance of confirmed block average: %f \n" % variance)
                    print("\n")

                    ########produced blocks############    
                    print("produced blocks: %d \n" %numblocks)
                    if(numblocks > 0):
                        avg = numblocks / float(len(listnumblocks))
                        variance = statistics.pvariance(listnumblocks,avg)
                        print("average of the produced blocks: ", avg)
                        print("variance of the produced blocks: ", variance)
                    print("\n")

                    ##########all block produced with the same if that a confirme block######
                    print("all block produced with the same id that a confirmed block: %d\n" %allblockswithconfirmed)
                    if(allblockswithconfirmed > 0):
                        avg = allblockswithconfirmed / float(len(listallblockwithconfirmed))
                        variance = statistics.pvariance(listallblockwithconfirmed,avg)
                        print("average of the all block produced with the same id that a confirmed block: ", avg)
                        print("variance of the all block produced with the same id that a confirme block: ", variance)
                    print("\n")

                    ##########main chain produced block#######
                    print("main chain produced block: %d \n" %mainchainProducedBlock)
                    if(mainchainProducedBlock > 0):
                        avg = mainchainProducedBlock / float(len(listmainchainProducedBlock))
                        variance = statistics.pvariance(listmainchainProducedBlock,avg)
                        print("average of the main chain produced block: ", avg)
                        print("variance of the main chain produced block: ", variance)
                    print("\n")

                    ########confirmation block number#########
                    #print("Confirmation Blocks number: %d\n" %numblockstable)
                    if(numblockstable > 0):
                        avg = numblockstable / float(len(listnumblockstable))
                        variance = statistics.pvariance(listnumblockstable,avg)
                        print("average of the confirmation block number: ", avg)
                        print("variance of the confirmation block number: ", variance)
                    print("\n")

                    print("Round number: %d" %numround)
                    print("\n")                    

                    ##########sucessful rafle number#########
                    print("successful raffle number: %d \n" %numsuc)
                    if(numsuc > 0):
                        avg = numsuc / float(len(listnumsuc))
                        variance = statistics.pvariance(listnumsuc, avg)
                        print("average of the success number: ", avg)
                        print("variance of the average sucess number: ", variance)
                    print("\n")




                    
                    
                    

                    
                                      

                    
                    
                    
                    
                    
                     
                    

                    
                    


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
                    numsuc = int(reply[9])
                    mainchainProducedBlock = mainchainProducedBlock + int(reply[10])
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
                    print("successful rafle number: %d \n" % numsuc)
                    print("main chain produced block: %d \n" %mainchainProducedBlock)
                else:
                    print("explorer command failed")

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
                print("Total: ", len(peers))                    
            else:
                print("Unknown command")            

        except zmq.Again:
            print("Command failed")
        sys.exit(0)
        reqsocket.close(linger=0)
        ctx.term()


    sys.exit(0)