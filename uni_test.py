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
    while(count < 11):
        if not locked:
            os.system("./blockchain-cli startmining")
            start = timer()
            locked = True

        if sqldb.getLastBlockIndex()==(100*count) and sqldb.getLastBlockIndex()>1:
            os.system("./blockchain-cli stopmining")     
            end = timer()
            time_result = end - start
            print('Para um' ,parameter.timeout, time_result)
            locked = False
            results.write(str(parameter.timeout) + ',' + str(time_result) + '\n')
            count = count + 1
    os.system("./blockchain-cli exit")
            

def quantityofforks():
    return NotImplemented

def timetosync():
    return NotImplemented


if __name__ == '__main__':

    timetocreateblocks()
