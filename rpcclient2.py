#!/usr/bin/env python

import zmq
import sys
from messages import *
import parameter
import hashlib
import time
import datetime
import statistics
import logging

#logging.basicConfig(filename = 'testenode.log',filemode ="w", level = logging.DEBUG, format =" %(asctime)s - %(levelname)s - %(message)s")
if __name__ == '__main__':
    help_string = '''usage: %s [-h]
        <command> [<args>]

Blockchain RPC client

These are the commands available:

getlastblock        logging.info the last block info
getblock <index>    logging.info the block info with index <index>
getblocks <list>    logging.info the blocks info from index <list>
startmining         Start the miner thread
stopmining          Stop the miner thread
addbalance <quantity> Add <quantity> of coins
addblock <list>     Add block manually from <list> [index, round]
addpeer <ip>        Add <ip> to the node peers list
removepeer <ip>     Remove <ip> to the node peers list
getpeerinfo         logging.info the peers list
exit                Terminate and exit the node.py program running
''' 

    if len(sys.argv) >= 2:
        try:
            if(MSG_MONITOR == sys.argv[1]):
                ctx = zmq.Context.instance()
                reqsocket = ctx.socket(zmq.REQ)
                reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                logging.info("produce transaction node: "+str(sys.argv[2]))

                reqsocket.send_multipart([MSG_FMINE, str(0)])
                logging.info(str(reqsocket.recv_string()))

                reqsocket.send(MSG_CONNECT)
                logging.info(str(reqsocket.recv_string()))
            
            elif(MSG_STARTPEER == sys.argv[1]):
                stake = parameter.numStake
                peers = parameter.peers
                i = 0
                startTime = float(time.mktime(datetime.datetime.now().timetuple()))
                while(i < len(peers)):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    logging.info(str(peers[i]))
                    reqsocket.connect("tcp://%s:9999" % peers[i])    
                    try:
                        #peer connect
                        reqsocket.send_multipart([MSG_CONNECT,str(startTime)])
                        logging.info(str(reqsocket.recv_string()))

                        #time.sleep(2)
                        #stake node
                        h = hashlib.sha256(str(peers[i])).hexdigest()            
                        s = stake[1][h][0]            
                        reqsocket.send_multipart([MSG_STAKE, str(s)])
                        logging.info(str(reqsocket.recv_string()))
                        
                    except zmq.Again:
                        logging.info("Command failed")                
                    reqsocket.close(linger=0)
                    ctx.term()
                    i = i + 1

            elif(MSG_TRANS == sys.argv[1]):
                peers = parameter.peers
                numtrans = 0
                listnumtrans = []
                numtavg = 0
                listnumtavg = []
                i = 0
                while (i < len(peers)):
                    try:                         
                        ctx = zmq.Context.instance()
                        reqsocket = ctx.socket(zmq.REQ)
                        reqsocket.setsockopt(zmq.RCVTIMEO, 5000)    
                        reqsocket.connect("tcp://%s:9999" % peers[i])
                        logging.info("Transmission for node : "str(peers[i]))
                        reqsocket.send_multipart([MSG_TRANS,sys.argv[2]])
                        reply = reqsocket.recv_pyobj()
                        if(reply):
                            numtrans = numtrans + reply[0]
                            listnumtrans = listnumtrans + [int(reply[0])]

                            numtavg = numtavg + reply[1]
                            listnumtavg = listnumtavg + [int(reply[1])]
                    except Exception as e:
                            logging.info(str(e))
                    i = i + 1

                avgtrans = float(numtrans) / len(listnumtrans)
                variance = statistics.pvariance(listnumtrans,avgtrans)

                avgtavg = float(numtavg) / len(listnumtavg)
                variancetavg = statistics.pvariance(listnumtavg,avgtavg)
                for k in listnumtrans:
                    logging.debug(str(k))
                logging.info("total transmission: %d" %numtrans)
                logging.info("avg transmission: "+str(avgtrans))
                logging.info("variance: "+str(variance))
                logging.info("\n")

                logging.info("propagation time / round time: "+str(avgtavg))
                logging.info("variance: "+str(variancetavg))

                
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
                            logging.info("Explorer node : "+str(peers[i]))
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
                            logging.info("confirmed block by node %s : %d" %(peers[i],int(reply[6])))
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
                            logging.info("produced block in main chain by node %s: %d" %(peers[i],int(reply[10])))
                            logging.info("all produced block with a confirmed block: %d" %(reply[11]))
                        except Exception as e:
                            logging.info(str(e))
                        i = i + 1

                    #########sync calls###############
                    logging.info("sync function calls number in the network view: %d" % callsync)
                    if(callsync > 0):
                        avg = callsync / float(len(listcallsync))
                        variance = statistics.pvariance(listcallsync, avg)
                        logging.info("average of the sync function calls:"+str(avg))
                        logging.info("variance of the sync function calls:"+str(variance))
                    logging.info("\n")

                    #########reversions number########
                    logging.info("Reversions number in the network view: %d \n" % callsyncrev)
                    if(callsyncrev > 0):
                        avg = callsyncrev / float(len(listcallsyncrev))
                        variance = statistics.pvariance(listcallsyncrev, avg)
                        logging.info("average of the reversions number: "+str(avg))
                        logging.info("variance of the reversions number:"+str(variance))
                    logging.info("\n")

                    #########reversed blocks number#######
                    logging.info("Reversed blocks number in the network view: %d \n" % numrevblock)
                    if(numrevblock > 0):
                        avg = numrevblock / float(len(listnumrevblock))
                        variance = statistics.pvariance(listnumrevblock,avg)
                        logging.info("average of reversed blocks number: "+str(avg))
                        logging.info("variance of the reversed blocks number: "+str(variance))
                    logging.info("\n")

                    #########received blocks number######
                    logging.info("Received blocks number: %d \n" % receivedblocks)
                    if(receivedblocks > 0):
                        avg = receivedblocks / float(len(listreceivedblocks))
                        variance = statistics.pvariance(listreceivedblocks, avg)
                        logging.info("average of the received blocks number: "+str(avg))
                        logging.info("variance of the received blocks number: "+str(variance))
                    logging.info("\n")

                    ##########late blocks number########
                    logging.i("late blocks number: %d \n" % lateblocks)
                    if(lateblocks > 0):
                        avg = lateblocks / float(len(listlateblocks))
                        variance = statistics.pvariance(listlateblocks, avg)
                        logging.info("average of the last blocks number: "+str(avg))
                        logging.info("variance of the last blocks number: "+str(variance))
                        if(ratelateblocks > 0):
                            avg = ratelateblocks / float(len(listratelateblocks))
                            variance = statistics.pvariance(listratelateblocks, avg)
                            logging.info("average of the rate late blocks: "+str(avg))
                            logging.info("variance of the rate late blocks: "+str(variance))
                    logging.info("\n")

                    if(avgconf > 0):
                        avg = avgconf / float(len(listAvgConf))
                        logging.info("Latency confirmation average in the network view (rounds): %f \n" % avg)
                        variance = statistics.pvariance(listAvgConf,avg)
                        logging.info("variance of confirmed block average: %f \n" % variance)
                    logging.info("\n")

                    ########produced blocks############    
                    logging.info("produced blocks: %d \n" %numblocks)
                    if(numblocks > 0):
                        avg = numblocks / float(len(listnumblocks))
                        variance = statistics.pvariance(listnumblocks,avg)
                        logging.info("average of the produced blocks: "+str(avg))
                        logging.info("variance of the produced blocks: "+str(variance))
                    logging.info("\n")

                    ##########all block produced with the same if that a confirme block######
                    logging.info("all block produced with the same id that a confirmed block: %d\n" %allblockswithconfirmed)
                    if(allblockswithconfirmed > 0):
                        avg = allblockswithconfirmed / float(len(listallblockwithconfirmed))
                        variance = statistics.pvariance(listallblockwithconfirmed,avg)
                        logging.info("average of the all block produced with the same id that a confirmed block: "+str(avg))
                        logging.info("variance of the all block produced with the same id that a confirme block: "+str(variance))
                    logging.info("\n")

                    ##########main chain produced block#######
                    logging.info("main chain produced block: %d \n" %mainchainProducedBlock)
                    if(mainchainProducedBlock > 0):
                        avg = mainchainProducedBlock / float(len(listmainchainProducedBlock))
                        variance = statistics.pvariance(listmainchainProducedBlock,avg)
                        logging.info("average of the main chain produced block: "+str(avg))
                        logging.info("variance of the main chain produced block: "+str(variance))
                    logging.info("\n")

                    ########confirmation block number#########
                    #logging.info("Confirmation Blocks number: %d\n" %numblockstable)
                    if(numblockstable > 0):
                        avg = numblockstable / float(len(listnumblockstable))
                        variance = statistics.pvariance(listnumblockstable,avg)
                        logging.info("average of the confirmation block number: "+str(avg))
                        logging.info("variance of the confirmation block number: "+str(variance))
                    logging.info("\n")

                    logging.info("Round number: %d" %numround)
                    logging.info("\n")                    

                    ##########sucessful rafle number#########
                    logging.info("successful raffle number: %d \n" %numsuc)
                    if(numsuc > 0):
                        avg = numsuc / float(len(listnumsuc))
                        variance = statistics.pvariance(listnumsuc, avg)
                        logging.info("average of the success number: "+str(avg))
                        logging.info("variance of the average sucess number: "+str(variance))
                    logging.info("\n")




                    
                    
                    

                    
                                      

                    
                    
                    
                    
                    
                     
                    

                    
                    


                elif(len(sys.argv) > 3):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                    logging.info("Explorer node : "+str(sys.argv[2]))
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
                    logging.info("Block confirmation average (block/round): %f \n" % avgconf)
                    logging.info("Confirmation Blocks number: %d" %numblockstable)
                    logging.info("produced blocks: %d \n" %numblocks)
                    logging.info("Sync function calls number: %d \n" % callsync)
                    logging.info("Reversions number: %d \n" % callsyncrev)
                    logging.info("Reversed blocks number: %d \n" % numrevblock)
                    if(callsyncrev > 0):
                        logging.info("Reversed blocks number average (Reversed blocks number / revertion): %f \n" % (float(numrevblock) / callsyncrev))
                    logging.info("Received blocks number : %d \n" % receivedblocks)
                    logging.info("Round number: %d \n" % numround)                                                            
                    logging.info("late blocks number: %d \n" % lateblocks)
                    logging.info("successful rafle number: %d \n" % numsuc)
                    logging.info("main chain produced block: %d \n" %mainchainProducedBlock)
                else:
                    logging.info("explorer command failed")

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
                        logging.info(str(reqsocket.recv_string()))
                        i = i + 1
                elif(len(sys.argv) > 2):
                    ctx = zmq.Context.instance()
                    reqsocket = ctx.socket(zmq.REQ)
                    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                    reqsocket.connect("tcp://%s:9999" % sys.argv[2])
                    reqsocket.send(sys.argv[1])
                    logging.info(str(reqsocket.recv_string()))
                    
                else:
                    logging.info("stopping command failed")
              
            elif(MSG_SHOWPEERS == sys.argv[1]):
                ctx = zmq.Context.instance()
                reqsocket = ctx.socket(zmq.REQ)
                reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
                reqsocket.connect("tcp://%s:9999" % sys.argv[2])                
                reqsocket.send(sys.argv[1])
                peers = reqsocket.recv_pyobj()
                logging.info("Node Peers: \n")
                for i in peers:
                    logging.info(i)
                logging.info("Total: "+str(len(peers)))                    
            else:
                logging.info("Unknown command")            

        except zmq.Again:
            logging.info("Command failed")
        sys.exit(0)
        reqsocket.close(linger=0)
        ctx.term()


    sys.exit(0)