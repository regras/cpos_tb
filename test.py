#!/usr/bin/env python
import consensus
import math
import parameter
import itertools
from decimal import Decimal
import sys
import time
import datetime
import hashlib
#find probability of k success (k nodes pass on network challenge and it produces a new block)

import logging

#logging.basicConfig(filename = 'testenode.log',filemode ="w", level = logging.DEBUG, format =" %(asctime)s - %(levelname)s - %(message)s")

def Combinations(m,n):
  
    # calcula o fatorial de m
    k = m
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1      
        k_fat *= cont  

    m_fatorial = k_fat
    # calcula o fatorial de n
    k = n
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1       
        k_fat *= cont   

    n_fatorial = k_fat
    # calcula o fatorial de m - n
    k = m-n
    k_fat = 1
    cont = 1
    while cont < k:
        cont += 1       
        k_fat *= cont   

    mn_fatorial = k_fat

    return (m_fatorial/(mn_fatorial * n_fatorial))

def sortition(userHash,stake):
    #p = cons.getTarget() / float(2**256)
    p = 0.0001
    logging.info("SUCCESS PROB: "+str(p))
    logging.info("STAKE: "+ str(stake))
    np = 1 - p
    q = int(userHash,16) / float(2**256)
    logging.info("Q: "+str(q))
    j = 0
    limitInf = Combinations(stake,0) * ((np)**(stake))
    limitSup = limitInf + Combinations(stake,1) * p * (np**(stake - 1))
    logging.info("LIMIT INF: "+str(limitInf))
    logging.info("LIMIT SUP: "+str(limitSup))
    while(q >= limitInf):
        j = j + 1
        limitInf = limitSup
        limitSup = limitSup + Combinations(stake,j+1) * (p**(j+1)) * (np**(stake - (j+1)))
    logging.info("RAFFLED NUMBER: "+str(j))
    return j

def calcproofHash(node,round,stake):
    user_header = str(round) + str(node) # user header
    user_hash = hashlib.sha256(user_header).hexdigest()

    subuser = sortition(user_hash,stake[0])
    return subuser
    

def calcBlocks(stake,node):
    raffled = 0
    prevTime = parameter.GEN_ARRIVE_TIME
    numRound = 1
    block = 0
    roundZero = 0
    sucRound = 0
    while(numRound <= 10):
        nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
        if((nowTime - prevTime) >= parameter.timeout):
            prevTime = nowTime
            round = int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/parameter.timeout))
            numRound = numRound + 1
            logging.info("Round: "+str(round))
            status = False
            total = 0
            sucRound = 0
            for h in range(0,len(node)):
                time.sleep(0.1)
                logging.info("Trying Node: "+str(node[h]))
                subuser = calcproofHash(node[h],round,stake[0][h])
                raffled = raffled + subuser
                if(subuser > 0):
                    block = block + 1
                    status = True
                    sucRound = sucRound + subuser

            
            if not status:
                roundZero = roundZero + 1
            logging.info("\n")
            logging.info("PARTIAL RAFFLED: "+str(raffled))
            logging.info("PARTIAL ROUNDS: "+str(numRound))
            logging.info("PARTIAL SUCESS/ROUND: %f" %(raffled/float(numRound)))
            logging.info("PARTIAL BLOCKs/ROUND: %f" %(block/float(numRound)))
            logging.info("PARTIAL zero/ROUND: %f" %(roundZero/float(numRound)))
            logging.info("%d SUCESS ON ROUND:  %d" %(sucRound,numRound))
        time.sleep(1)

    logging.info("Total SUCESS: %d" %raffled)
    logging.info("Total rounds: %d" %numRound)
    logging.info("Total blocks: %d" %block)
    logging.info("block/round: %f", block / float(numRound))
    logging.info("suc/round: %f", raffled / float(numRound))
    logging.info("Total round zero: %d" %roundZero)

          

def main():
    #calc each node stake
    con = 0.1
    stakeCon = 0.9
    nodes = 10
    W = 10000
    nodes = parameter.peers
    stake = parameter.numStake
    '''numStake = {}
    numNodesCon = int(math.floor(con * nodes))
    restNodes = nodes - numNodesCon
    if(numNodesCon > 0):
        stake1 = int(math.floor(stakeCon*(W)))
        stake2 = (W - stake1)
        flag1 = stake1 % numNodesCon
        flag2 = stake2 % restNodes
        stake1 = int(math.floor(float(stake1) / numNodesCon))
        stake2 = int(math.floor(float(stake2) / restNodes))
    else:
        stake1 = 0
        stake2 = W - nodes
    i = 0
    numStake[i] = {}
    j = 1
    for h in range(0,nodes):
        if(j <= numNodesCon):
            if(h == 1):
                numStake[i][h] = [stake1 + flag1]
            else:
                numStake[i][h] = [stake1]
        else:
            if(h == numNodesCon + 1):
                numStake[i][h] = [stake2 + flag2]
            else:
                numStake[i][h] = [stake2]
        j = j + 1
    p = float(1.5) / 10000
    node = [x for x in range(1,10+1)]'''
    calcBlocks(numStake,node)
    sys.exit()

if __name__ == '__main__':
    main()

        


