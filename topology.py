import parameter
import random
from operator import itemgetter
import pickle

import logging

#logging.basicConfig(filename = 'testenode.log',filemode ="w", level = logging.DEBUG, format =" %(asctime)s - %(levelname)s - %(message)s")
def defineNeighbors():
    peers = parameter.peers
    k = parameter.k
    neighbors = {}
    p = [j for j in peers]
    for ip in peers:
        if(ip in neighbors):
            limit = len(neighbors[ip])
        else:
            limit = 0
        #fpeer = False
        fneig = False        
        while limit < k:
            logging.info(str(limit))            
            if (len(p) == 1 and ip in p):
                p = []
            if(len(p) >= 1):
                index = random.randint(0, len(p) - 1)
                if p[index] != ip:
                    if (limit < k - 1) or fneig:
                        if ip not in neighbors:
                            neighbors[ip] = []
                        if p[index] not in neighbors[ip]:
                            if p[index] not in neighbors:
                                neighbors[p[index]] = []
                            if len(neighbors[p[index]]) < k :
                                neighbors[ip].append(p[index])                        
                                neighbors[p[index]].append(ip)
                                del p[index]                                
                                limit = limit + 1
                                #fpeer = True
            #else:
            #    fpeer = True

            if limit == k:
                break

            if(len(neighbors) > k + 1):
                list = [j for j in neighbors]
                index = random.choice(list)
                if index != ip:
                    #if (limit < k - 1) or fpeer:
                    if ip not in neighbors:
                        neighbors[ip] = []
                    if index not in neighbors[ip] and len(neighbors[index]) <= k:
                        neighbors[ip].append(index)                        
                        neighbors[index].append(ip)
                        limit = limit + 1
                        fneig = True 
            else:
                fneig = True
            #if ip in neighbors:
                #print neighbors
                #print fneig
                #print ip
                #print neighbors[ip]
                #print limit  
        if ip in p:
            id = p.index(ip)       
            del p[id]
    logging.info(str(neighbors))
    with open('peers.pkl', 'wb') as output:
        pickle.dump(neighbors,output,pickle.HIGHEST_PROTOCOL)
    
if __name__ == '__main__':
    defineNeighbors()
