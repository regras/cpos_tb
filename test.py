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
    p = 0.000001
    print("SUCCESS PROB: ", p)
    print("STAKE: ", stake)
    np = 1 - p
    q = int(userHash,16) / float(2**256)
    print("Q: ", q)
    j = 0
    limitInf = Combinations(stake,0) * ((np)**(stake))
    limitSup = limitInf + Combinations(stake,1) * p * (np**(stake - 1))
    print("LIMIT INF: ", limitInf)
    print("LIMIT SUP: ", limitSup)
    while(q >= limitInf):
        j = j + 1
        limitInf = limitSup
        limitSup = limitSup + Combinations(stake,j+1) * (p**(j+1)) * (np**(stake - (j+1)))
    print("RAFFLED NUMBER: ", j)
    return j

def calcproofHash(node,round,stake):
    user_header = str(round) + str(node) # user header
    user_hash = hashlib.sha256(user_header).hexdigest()

    subuser = sortition(user_hash,stake[0])
    return subuser
    

def calcBlocks(stake,node):
    raffled = {}
    numRound = 1
    while(numRound <= 10):
        nowTime = int(time.mktime(datetime.datetime.now().timetuple()))
        if((nowTime - prevTime) >= parameter.timeout):
            prevTime = nowTime
            round = int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/parameter.timeout))
            print("ROUND: ",round)
            raffled[round] = 0
            subuser = calcproofHash(node,round,stake)
            if(subuser > 0):
                raffled[round] = raffled[round] + subuser
                
            if not status:
                roundZero = roundZero + 1
            print("\n")
            print("RAFFLED ON ROUND: ", subuser)
                    
        time.sleep(parameter.timeout - (int(time.mktime(datetime.datetime.now().timetuple())) - nowTime))            

def main():
    calcBlocks(parameter.W,1)
    sys.exit()

if __name__ == '__main__':
    main()

        


