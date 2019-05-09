import parameter
import sqldb  
from timeit import default_timer as timer
import os

def timetocreateblocks():    
    start = timer()
    end = timer()
    locked = False
    #os.system("./node")
    results = open('results.txt', 'a')
    count = 1
    while(count < 2):
        if not locked:
            os.system("./blockchain-cli startmining")
            start = timer()
            locked = True

        #if sqldb.getLastBlockIndex()==(100*count) and sqldb.getLastBlockIndex()>1:
        if sqldb.quantityofBlocks()>(100*count) and sqldb.quantityofBlocks()>1:
            os.system("./blockchain-cli stopmining")     
            end = timer()
            time_result = end - start
            #print('dif', parameter.difficulty, 'timeout', parameter.timeout, time_result)
            locked = False
            results.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ','  + str(parameter.timeout) + ',' + str(time_result) + '\n')
            count = count + 1
    
    results.close()
    #os.system("./blockchain-cli exit")
            

def quantityofforks():
    results2 = open('forks.txt', 'a')
    forks = sqldb.getQuantityForks()
    results2.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ',' +  str(forks) + '\n')
    results2.close()

def quantityofchains():
    tree = sqldb.getallblocks()
    blocks = [[(b.index,b.hash), []] for b in tree]
    results = open('chains.txt', 'a')
    for i in blocks:
        for b in tree:
            if (i[0][1] == b.prev_hash):
                i[1].append([b.index, b.prev_hash, b.hash, b.round])
    
    chains = 1
    for r in blocks:
        value = len(r[1])
        if(value == 0):
            value = 1
        chains = chains * value
    
    results.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ',' + str(chains) + '\n')
    results.close()

def quantityofgaps():
    chain = sqldb.getallchain()
    results = open('gaps.txt', 'a')
    gaps = 0
    for i in range(1,len(chain)):
        gaps = (chain[i].round - chain[i-1].round)/parameter.timeout
        results.write(str(parameter.test_num_nodes) + ',' + str(parameter.difficulty) + ',' + str(parameter.timeout) + ','+ str(chain[i-1].index) +',' + str(chain[i].index) + ',' + str(gaps) + '\n')
    
    results.close()

def timetosync():
    return NotImplemented


if __name__ == '__main__':
    timetocreateblocks()
    quantityofforks()
    quantityofchains()
    quantityofgaps()
    os.system('./blockchain-cli exit')
