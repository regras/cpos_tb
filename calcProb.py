#!/usr/bin/env python
import consensus
import math
import parameter
import itertools
from decimal import Decimal
import sys
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

def pk_r(ps, pf, r):
    probK = {}
    x = 0
    r = int(r)
    while(x <= r):
        j = 0
        probK[x] = []
        countProbK = 0
        if(x == 0):
            probK[0] = []
            for i in range(0,parameter.NODES + 1):
                numComb = Combinations(parameter.NODES,i)
                p1 = numComb * (ps**i) * (pf**(parameter.NODES - i))
                probK[x].append(p1)
                countProbK = countProbK + p1 
        else:
            #while(countProbK <= 0.999):
            while(countProbK <= 0.999):
                print("k: ", j)
            #while(j <= parameter.NODES ** (x + 1)):
                pj = 0
                #len_x = len(probK[x-1])
                if(j == 0):
                    start = 1
                else:
                    start = int(math.ceil(float(j)/float(parameter.NODES)))
                    #print(start)
                
                for i in range(start,len(probK[x-1])):
                #for i in range(start, parameter.NODES**x + 1):
                    numComb = Combinations(i*parameter.NODES, j)
                    pj = pj + (numComb * (ps**j) * (pf**(i * parameter.NODES - j))) * probK[x-1][i]
                if(j <= parameter.NODES):
                    numComb = Combinations(parameter.NODES,j)
                    #print("pj_0:", (numComb * (ps**j) * (pf**(parameter.NODES - j))) * probK[x-1][0])
                    pj = pj + (numComb * (ps**j) * (pf**(parameter.NODES - j))) * probK[x-1][0]
                    '''z = 1
                    pz = 0
                    while(z <= x - 1):
                        pi = 0
                        #for i in range(start,parameter.NODES**(x - z)):
                        for i in range(start, len(probK[x-(z+1)])):
                            numComb = Combinations(i*parameter.NODES,j)
                            pi = pi + (numComb * (ps**j) * (1 - ps)**(i*parameter.NODES - j)) * probK[x-(z+1)][i]

                        prodP0 = 1
                        for i in range(1, z + 1):
                            prodP0 = prodP0 * probK[x - i][0]
                        pi = pi * prodP0
                        pz = pz + pi
                        z = z + 1
                    #All zeros
                    prodP0 = 1 
                    for i in range(0, x):
                        prodP0 = prodP0 * probK[i][0]
                    numComb = Combinations(parameter.NODES, j)
                    pi = numComb * (ps**j) * ((1-ps)**(parameter.NODES - j)) * prodP0
                    pz = pz + pi
                    pj = pj + pz'''
                if(pj != 0):
                    probK[x].append(pj)
                    countProbK = countProbK + pj
                if (j == 100 or pj == 0):
                    break
                j = j + 1
        print("prob sum round %f: %f" %(x, countProbK))
        x = x + 1
    return probK
def numBlockExpected(pk,n,r):
    numBlock = 0
    for i in range(0,r + 1):
        numBlock = numBlock + ((Decimal(1) - (pk[i][0] + pk[i][1])) * n)
    return numBlock 

def probFork(pk,pnf,psn,r):
    print("pnf")
    print(pnf)
    print("1-pnf")
    print(1-pnf)
    if(r >= 1):
        k = 1
        pf_r = 0
        NumRound = 0
        while(k <= len(pk[r-1]) - 1):
            print(len(pk[r-1]))
        #while(k <= parameter.NODES**r):
            pf_i = 0
            numRound_i = 0
            for i in range(0,k):
                numComb = Combinations(k,i)
                pf_i = pf_i + numComb * (((1 - pnf) ** (k-i)) * (pnf ** i))

                numComb = Combinations(k,i)
                numRound_i = numRound_i + numComb * ((psn) ** (k-i)) * ((1 - psn) ** i)
           
            pf_i = pk[r-1][k] * pf_i
            pf_r = pf_r + pf_i
            NumRound = NumRound + pk[r-1][k] * int(math.ceil(float(1)/float(numRound_i)))
            k = k + 1

        #start P0_r-1 part. This part depends of the r_2's success. If the r_2 have nothing success
        # the process uses the r_3 and repeat until find one round that have any success
        # or find the round 0.
        '''x = 1
        pf0 = 0
        while(x <= r - 1):
            pf0_k = 0
            for k in range(1, len(pk[r-(x+1)])):
            #for k in range(1,(parameter.NODES**(r-x)) + 1):
                pk_k = pk[r-(x+1)][k]
                pf0_i = 0
                for i in range(1,k):
                    numComb = Combinations(k,i)
                    pf0_i = pf0_i + numComb * ((1-pnf) ** (k-i)) * (pnf ** i)
                pf0_k = pf0_k + (pk_k * pf0_i)

            p0 = 1
            for j in range(1,x + 1):
                p0 = p0 * pk[r-j][0]
        
            pf0 = pf0 + pf0_k * p0
            x = x + 1'''

        #If nothing nodes mine any block since round zero until round r-1 we have this case:
        #P0_(r-1) * P0_(r-2) * P0_(r-3) * P0_(r-4) ... P0_(2) * P0_(1) * P0(0)
        #In this case, we have the same fork's probability of the round zero in round r
        # So it is: (1-pnf) * [P0_(r-1) * P0_(r-2) * P0_(r-3) * P0_(r-4) ... P0_(2) * P0_(1) * P0(0)]
        '''p0 = 1
        for j in range(1,r + 1):
            p0 = p0 * pk[r-j][0]

        pf0 = pf0 + (1 - pnf) * p0'''
        pf0 = (1-pnf) * pk[r-1][0]
        NumRound0 = int(math.ceil(float(1)/float(psn))) * pk[r-1][0]
             
        #So the fork's probability of the round r is pf0 + pf_r
        pf_r = pf_r + pf0
        NumRound = NumRound + NumRound0
    else:
        pf_r = 1 - pnf
        NumRound = int(math.ceil(float(1)/float(psn)))

    return pf_r, NumRound

def main():

    r = input("Digite (r) para calcular pk:")
    
    cons = consensus.Consensus()
    ps = Decimal(cons.getTarget())/((2**(256) - 1))
    print("ps")
    print(ps)
    pf = 1 - ps
    print("pf")
    print(pf)

    pk = pk_r(ps,pf,r)
   
    for i in range(0, parameter.NODES + 1):
        print("rodada r = 0 e k = %d" % i)
        print(pk[0][i])

    for i in range(1, r + 1):
        for j in range(0, len(pk[i])):
        #for j in range(0, parameter.NODES**(i + 1) + 1):
            print("rodada r = %d e k = %d" %(i,j))
            print(pk[i][j])

    pnf = (pf ** parameter.NODES) + (parameter.NODES * ps * (pf ** (parameter.NODES - 1)))
    print(pnf)

    #calc success probability to n nodes in one chain
    pns = 1 - (1 - ps) ** parameter.NODES
    print(pns)
    while(r != -1):
        r = input("Digite (r) para probabilidade de fork:")
        if(r >= 0):
            Pfork, NumRound = probFork(pk,pnf, pns, r)
            numBlock = numBlockExpected(pk,parameter.NODES,r)
            print("Fork probability on round : %d" % r)
            print(Pfork)
            print("Expected round number between two blocks:")
            print(NumRound)
            print("Expected total block:")
            print(numBlock)
    
    sys.exit()

if __name__ == '__main__':
    main()

        


