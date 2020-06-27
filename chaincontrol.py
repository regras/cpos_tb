#!/usr/bin/env python
from collections import defaultdict
import json
import time
import datetime
import parameter
import sqldb
import threading
import math

'''def removeLeaf(self,pos):
    print("remove chain with head")
    print(self.leaf[pos][0].leaf_head)
    print("remove chain with prev_head")
    print(self.leaf[pos][0].leaf_prev_head)
    print("index")
    print(self.leaf[pos][0].leaf_index)
    print("hash")
    print(self.leaf[pos][0].leaf_hash)
    #sqldb.setLogFork(self.leaf[pos][0].leaf_head,'0')
    #sqldb.setLogFork(self.leaf[pos][0].leaf_head, 0, 0, 0, self.leaf[pos][0].leaf_index, self.leaf[pos][0].leaf_hash)
    status = sqldb.removeChain(self.leaf[pos][0].leaf_hash)
    if(status):
        print("chain removed with success")
        del self.leaf[pos]
    else:
        print("chain not removed with success. Fork point not found.")'''
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

def probTree(r,x,z,blockchain):
    t = r
    d = 1
    #zr0 = calcZr(None,0)
    tree = {}
    #print("ROUND: %d" %x)
    #print("ZRO: %f" %zr0)
    while (t <= x - 1):
        status = False
        if(d == 1):
            tree[1] = [z[t],3]
            status = True
        else:
            for i in range(2**(d-2), 2**(d-1)):
                if(i in tree.keys()):
                    father = tree[i][1]
                    if(father == 1 or blockchain[t] == None):
                        if(num_blocks_between(t,x-1,blockchain) > 0):
                            if(blockchain[t]):
                                tree[2*i] = [z[t],3]
                                tree[2*i+1] = [1 - z[t],4]
                            else:
                                tree[2*i] = [z[t],1]
                                tree[2*i+1] = [1 - z[t],2]
                            status = True      
                    else:
                        if(father == 2):
                            j = int(math.floor(i/2))
                            while(j >=1 and tree[j][1] == 2):
                                j = int(math.floor(j/2))
                            if tree[j][1] == 1:
                                tree[2*i+1] = [1 - z[t],4]
                        tree[2*i] = [z[t],3]
                        status = True
        if(status):
            d = d + 1 
        t = t + 1        
    #print(tree)
    return tree

'''def probTree(r,x,z,blockchain):
    t = r
    d = 1
    zr0 = calcZr(None,0)
    tree = {}
    print("ROUND: %d" %x)
    print("ZRO: %f" %zr0)
    while (t <= x - 1):
        status = False
        if(d == 1):
            tree[1] = z[t]
            status = True
        else:
            for i in range(2**(d-2), 2**(d-1)):
                if(i in tree.keys()):
                    father = tree[i]
                    if(father == zr0 or z[t] == zr0):
                        if(num_blocks_between(t,x-1,z) > 0):
                            tree[2*i] = z[t]
                            tree[2*i+1] = 1 - z[t]
                            status = True      
                    else:
                        if(father == 1 - zr0):
                            j = int(math.floor(i/2))
                            while(j >=1 and tree[j] == 1 - zr0):
                                j = int(math.floor(j/2))
                            if tree[j] == zr0:
                                tree[2*i+1] = 1 - z[t]
                        tree[2*i] = z[t]
                        status = True
        if(status):
            d = d + 1 
        t = t + 1        
    print(tree)
    return tree '''

def reversionProb(r,x,z,blockchain):
    tree = probTree(r,x,z,blockchain)
    if(tree):
        j = max(tree)
        d = 1
        while j > 2**(d) - 1:
            d = d + 1
        
        #print("nivel: %d" %d)
        phr = 0
        for i in range(2**(d-1),2**(d)):
            phri = 1
            if(i in tree.keys()):
                phri = phri * tree[i][0]
                j = int(math.floor(i/2))
                while(j >= 1):
                    phri = phri * tree[j][0]
                    j = int(math.floor(j/2))
                phr = phr + phri
        #print("PHR: %f" %phr)
        return phr
    return 1
    
def num_blocks_between(r,t,blockchain):
    if(blockchain):
        maxBlockchain = max(blockchain)
        num = 0
        #zr0 = calcZr(None,0)
        if(t <= maxBlockchain):
            for k in range(r,t + 1):
                if(not blockchain):
                    num = num + 1
        else:
            print("invalid position")
        return num
    return 0

def all_not_gap_between(r,t,z,blockchain):
    maxZ = max(z)
    maxBlockchain = max(blockchain)
    prodZ = 1
    if(t <= maxZ and t <= maxBlockchain):
        for k in range(r,t + 1):
            if(blockchain[t]):
                prodZ = prodZ * z[t]
    else:
        print("invalid position")
    return prodZ

def bkpreversionProb(r,x,blockchain,z):
    phr = 0
    phri = 1
    new_gap = False
    numBlock = 0
    t = r
    while t < x:
        print("numBlock: %d" %numBlock)
        print("phri: %f" %phri)
        if(blockchain[t]):
            if(numBlock <= num_blocks_between(r,x-1,blockchain)):
                phri = phri * z[t]
                numBlock = numBlock + 1
        elif not new_gap and num_blocks_between(t+1,x-1,blockchain) > 0:
            gap_pos = t
            new_gap = True
        if t == x - 1:
            phr = phr + phri
            if new_gap:
                t = gap_pos + 1
                new_gap = False
                phri = all_not_gap_between(r,t-1,z,blockchain)*z[t-1]
                numBlock = num_blocks_between(r,t-1,blockchain) + 1
            else:
                t = t + 1
        else:
            t = t + 1
    return phr


def calcZr(h,numSuc):
    p = float(parameter.tal) / float(parameter.W)
    if(numSuc == 0):
        hpr = 1
    else:
        hpr = int(h,16) / float(2**256)
    qr = 0
    for k in range(0,numSuc+1):
        comb = Combinations(parameter.W,k)
        qr = qr + comb*(p**k)*((1-p)**(parameter.W - k))
    qr = 1 - qr
    #print("Qr: %f" %qr)
    #print("hpr: %f" %hpr)
    zr = hpr * qr
    #print("zr: %f" %zr)
    return zr

def updateChainView(idChain, block, subUser):
    if(sqldb.blockIsMaxIndex(block.index)):
        print("IS MAXINDEX")
        sqldb.writeChainLeaf(idChain, block, subUser)
        return True
    elif(not sqldb.blockIsMaxIndex(block.index)):
        status,round = sqldb.verifyRoundBlock(block.index,block.round)
        if(status):
            if(((round == block.round) and sqldb.blockIsPriority(block.index,block.proof_hash))
            or (block.round < round)):
                print("ISLEAF")
                print("NOT MAXINDEX")
                sqldb.removeAllBlocksHigh(block.index, block.proof_hash)
                sqldb.writeChainLeaf(idChain, block, subUser)
                return True
            else:
                return False
    #elif(not sqldb.blockIsLeaf(block.index, block.prev_hash)):
    #    if(sqldb.blockIsPriority(block.index,block.hash)):
    #        print("NOT LEAF")
    #        print("NOT MAXINDEX")
    #        sqldb.createNewChain(block)
    #        sqldb.removeAllBlocksHigh(block.index, block.hash)
    #        return True
    #    else:
    #        return False
    else:
        print("not insert new block")
        return False
            
def addBlockLeaf(block=None,subUser=None,sync=False):
    #inserting block on the chain's top
    if(not sync):
        idChain = sqldb.getIdChain(block.prev_hash)
        print("idChain:")
        print(idChain)
        if(idChain):
            status = updateChainView(idChain, block, subUser)
            if(status):
                print("new block inserted")
                return True
            else:
                print("new block not inserted")
                return True
        else:
            print("blockchain not found. not sync?")
            return False
        
