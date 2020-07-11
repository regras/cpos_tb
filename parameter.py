import math
import random
import time
import datetime
# -*- coding: utf-8 -*-

# Initial Arrive Time
GEN_ARRIVE_TIME = 1573486728
#GEN_ARRIVE_TIME = time.mktime(datetime.datetime.now().timetuple())
# Threshold that the blockchain can grown and accept one previous block with the best round.
THRESHOLD = 2

# Time in seconds
timeout = 30
# difficulty

### Test Variables ###
num_block_created = 0
test_num_nodes = 10

FIRST_HASH = "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"

AVG_LATENCY = timeout / 2

TOLERANCY = timeout * 1.4

roundTolerancy = 0

betha = 0.00001

TEST = 100

NODES = 2

W = 10000 #all network coins

q = 0 #attackers probability

hW = int(W * float(1 - q)) #honest coins

tal = 10 #proposer parameter

difficulty = float(math.log(W,2) - math.log(tal,2)) 


def defineStake(nodes):
    numStake = {}
    i = 16
    rate = {}
    rate[4] = [0.10,0.90]
    rate[5] = [0.10,0.70]
    rate[6] = [0.10,0.50]
    rate[7] = [0.50,0.90]
    rate[8] = [0.50,0.70]
    rate[9] = [0.50,0.50]
    rate[10] = [0.10,0.90]
    rate[11] = [0.10,0.70]
    rate[12] = [0.10,0.50]
    rate[13] = [0.50,0.90]
    rate[14] = [0.50,0.70]
    while(i == 16):
        #print(nodes)
        if(i <= 3):
            stakeTotal = W - nodes
            stake = random.randint(0,stakeTotal) + 1
            numStake[i] = {}
            j = 1
            for h in range(1,nodes+1):
                if(j == nodes):
                    numStake[i][h] = [stakeTotal + 1]
                else:
                    numStake[i][h] = [stake]
                stakeTotal = stakeTotal - (stake - 1)
                stake = random.randint(0,stakeTotal) + 1 
                j = j + 1
                                
        elif(i > 3 and i <= 9):
            con = rate[i][0]
            stakeCon = rate[i][1]
            numNodesCon = int(math.floor(con * nodes))
            restNodes = nodes - numNodesCon
            if(numNodesCon > 0):
                stake1 = int(math.floor(stakeCon*(W)))
                stake2 = (W - stake1) - restNodes
                stake1 = stake1 - numNodesCon
            else:
                stake1 = 0
                stake2 = W - nodes
            numStake[i] = {}
            for h in range(1,nodes+1):
                if(h <= numNodesCon):
                    if(h == numNodesCon):
                        numStake[i][h] = [stake1 + 1]
                    else:
                        stake = random.randint(0,stake1) + 1
                        numStake[i][h] = [stake]
                        stake1 = stake1 - (stake - 1)
                else:
                    #print(stake2)
                    if(h == nodes):
                        numStake[i][h] = [stake2 + 1]
                    else:
                        stake = random.randint(0,stake2) + 1
                        numStake[i][h] = [stake]
                        stake2 = stake2 - (stake - 1)                
                #print(numStake)    
        
        elif(i > 9 and i <= 14):
            con = rate[i][0]
            stakeCon = rate[i][1]
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
            numStake[i] = {}
            j = 1
            for h in range(1,nodes+1):
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
            #print(numStake) 
        elif(i == 15):
            stake = W - (nodes - 1)
            numStake[i] = {}
            for h in range(1,nodes+1):
                if(h == 1):
                    numStake[i][h] = [stake]
                else:
                    numStake[i][h] = [1]

        elif(i == 16):
            stake = hW / nodes
            numStake[i] = {}
            for h in range(1,nodes+1):
                numStake[i][h] = [stake]

        i = i + 1
    return numStake
