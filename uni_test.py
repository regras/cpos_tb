#!/usr/bin/env python
import parameter
import sqldb  
from timeit import default_timer as timer
import os
import calculation
import time
import sys
#import node
def timetocreateblocks(node):   
    time.sleep(2) 
    start = timer()
    end = timer()
    locked = False
    #os.system("./node")
    #results = open('results.txt', 'a')
    count = 0
    numBlocks = 0
    lastForks = {}
    lastBlockSimulation = 0
    print("Call timetocreateBlocks function!")
    while(count <= 0):
        if not locked:
            time.sleep(1)
            os.system("./blockchain-cli startmining")
            start = timer()
            locked = True

        #if sqldb.getLastBlockIndex()==(100*count) and sqldb.getLastBlockIndex()>1:
        quantityBlocks = node.commitBlock(message=[lastBlockSimulation],t=5)
        node.releaseCommitBlock()
        print("QUANTITY BLOCKS")
        print(quantityBlocks)
        if(quantityBlocks >= parameter.TEST):
        #if(sqldb.quantityofBlocks(lastBlockSimulation) >= parameter.TEST):
            os.system("./blockchain-cli stopmining")   
            end = timer()
            #time_result = end - start
            #print('dif', parameter.difficulty, 'timeout', parameter.timeout, time_result)
            locked = False
            lastForks, newBlocks = node.commitBlock(message=[start,end,lastForks,numBlocks],t=6)
            node.releaseCommitBlock()
            #lastForks, newBlocks = calculation.calcParameters(start,end,lastForks, numBlocks)
            numBlocks = numBlocks + newBlocks
            print("numBlocks")
            print(numBlocks)
            print("count")
            print(count)
            lastBlockSimulation = node.commitBlock(message=[lastBlockSimulation], t=7)
            node.releaseCommitBlock()
            #lastBlockSimulation = sqldb.getLastStableBlock(lastBlockSimulation)
            print("lastBlockSimulation")
            print(lastBlockSimulation)
            count = count + 1
            time.sleep(1)
        else:
            time.sleep(30)
    
    #results.close()
    #os.system("./blockchain-cli exit")
            

#def quantityofforks():
#    results2 = open('forks.txt', 'a')
#    forks = sqldb.getQuantityForks()
#    results2.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ',' +  str(forks) + '\n')
#    results2.close()

#def quantityofchains():
#    tree = sqldb.getallblocks()
#    blocks = [[(b.index,b.hash), []] for b in tree]
#    results = open('chains.txt', 'a')
#    for i in blocks:
#        for b in tree:
#            if (i[0][1] == b.prev_hash):
#                i[1].append([b.index, b.prev_hash, b.hash, b.round])
    
 #   chains = 1
 #   for r in blocks:
 #       value = len(r[1])
 #       if(value == 0):
 #           value = 1
 #       chains = chains * value
    
 #   results.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ',' + str(chains) + '\n')
 #   results.close()

#def quantityofgaps():
#    chain = sqldb.getallchain()
#    results = open('gaps.txt', 'a')
#    gaps = 0
#    for i in range(1,len(chain)):
#        gaps = (chain[i].round - chain[i-1].round)/parameter.timeout
#        results.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ','+ str(chain[i-1].index) +',' + str(chain[i].index) + ',' + str(gaps) + '\n')
    
#    results.close()

#def timetosync():
#    return NotImplemented
#def main():
#    parser = argparse.ArgumentParser(description='Automatic Simulation of PoSTD protocol')
#    parser.add_argument('-n', '--node', metavar='node', dest='node',
#                        help='Specify a node object')
#    args = parser.parse_args()
#    cfgparser = SafeConfigParser({'node':args.node})
#    if cfgparser.read(args.config_file):
#        args.node = cfgparser.get('node','node')
#        node = args.node
        #node = pickle.loads(node)
#        print node

#if __name__ == '__main__':
    #timetocreateblocks()
    #quantityofforks()
    #quantityofchains()
    #quantityofgaps()
    #os.system('./blockchain-cli exit')