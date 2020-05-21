from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info

from functools import partial
from time import sleep
from random import shuffle
import sys, os
import time
import random
import parameter
import math

# Sample usage
# sudo python simpleNet.py <n>
# n: number of hosts

# file directory path to mount private dirs
dir_path = os.path.dirname(os.path.realpath(__file__))
#mode = 1 (Aleatorio)
#mode = 2 (x% do stake concentrado com y% dos participantes)
#mode = 3 (stake dividido igualmente entre os participantes)
#mode = 4 (stake concentrado em apenas um participante)
#mode = 5 (x% do stake concentrado com y% dos participantes e distribuicao igual do stake)
def testHostWithPrivateDirs(number=10, message=[0.1, 0.5], mode=5):
    "Test bind mounts"
    topo = SingleSwitchTopo( number )
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    startServer(net,message,mode)
    CLI( net )
    stopServer(net.hosts)
    net.stop()

def startServer(net,message,mode):
    """ Start node.py process passing all hosts ip addresses """
    numStake = {}
    if(mode == 1):
        stakeTotal = parameter.W - len(net.hosts)
        stake = random.randint(0,stakeTotal) + 1
        i = 1
        for h in net.hosts:
            if(i == len(net.hosts)):
                numStake[h.IP()] = [stakeTotal + 1]
            else:
                numStake[h.IP()] = [stake + 1]
            stakeTotal = stakeTotal - (stake - 1)
            stake = random.randint(0,stakeTotal) + 1 
            i = i + 1                 
        
    elif(mode == 2):
        con = message[0]
        stakeCon = message[1]
        numNodesCon = int(math.floor(con * len(net.hosts)))
        restNodes = len(net.hosts) - numNodesCon
        if(numNodesCon > 0):
            stake1 = int(math.floor(stakeCon*(parameter.W)))
            stake2 = (parameter.W - stake1) - restNodes
            stake1 = stake1 - numNodesCon
        else:
            stake1 = 0
            stake2 = parameter.W - len(net.hosts)
        print(stake2)
        print(stake1)
        i = 1
        for h in net.hosts:
            if(i <= numNodesCon):
                if(i == numNodesCon):
                    numStake[h.IP()] = [stake1 + 1]
                else:
                    stake = random.randint(0,stake1) + 1
                    numStake[h.IP()] = [stake]
                    stake1 = stake1 - (stake - 1)
            else:
                print(stake2)
                if(i == len(net.hosts)):
                    numStake[h.IP()] = [stake2 + 1]
                else:
                    stake = random.randint(0,stake2) + 1
                    numStake[h.IP()] = [stake]
                    stake2 = stake2 - (stake - 1)
            i = i + 1
        print(numStake)    
    elif(mode == 3):
        stake = parameter.W / len(net.hosts)
        for h in net.hosts:
            numStake[h.IP()] = [stake]

    elif(mode == 4):
        stake = parameter.W - (len(net.hosts) - 1)
        i = 1
        for h in net.hosts:
            if(i == 1):
                numStake[h.IP()] = [stake]
            else:
                numStake[h.IP()] = [1]
            i = i + 1

    elif(mode == 5):
        con = message[0]
        stakeCon = message[1]
        numNodesCon = int(math.floor(con * len(net.hosts)))
        restNodes = len(net.hosts) - numNodesCon
        if(numNodesCon > 0):
            stake1 = int(math.floor(stakeCon*(parameter.W)))
            stake2 = (parameter.W - stake1)
            flag1 = stake1 % numNodesCon
            flag2 = stake2 % restNodes
            stake1 = int(math.floor(float(stake1) / numNodesCon))
            stake2 = int(math.floor(float(stake2) / restNodes))
        else:
            stake1 = 0
            stake2 = parameter.W - len(net.hosts)
        i = 1
        for h in net.hosts:
            if(i <= numNodesCon):
                if(h.IP() == '10.0.0.1'):
                    numStake[h.IP()] = [stake1 + flag1]
                else:
                    numStake[h.IP()] = [stake1]
            else:
                if(i == numNodesCon + 1):
                    numStake[h.IP()] = [stake2 + flag2]
                else:
                    numStake[h.IP()] = [stake2]
            i = i + 1
        print(numStake) 

    for h in net.hosts:
            o = net.hosts[:]
            o.remove(h)
            ips = [x.IP() for x in o]
            shuffle(ips)
            peers = ' '.join(ips)
            info('*** Blockchain node starting on %s\n' % h)
            h.cmd('nohup python node.py -i', h.IP(), '-p 9000 -s %s --peers %s &' %(numStake[h.IP()][0], peers))
            

def stopServer(hosts):
    """ Stop the node.py process through rpcclient """
    for h in hosts:
        #
        h.cmd('rpc/rpcclient.py exit')
        info('*** Blockchain node stopping on %s\n' % h)

if __name__ == '__main__':
    setLogLevel( 'info' )
    if len(sys.argv) >= 2:
        testHostWithPrivateDirs(int(sys.argv[1]))
    else:
        testHostWithPrivateDirs()
    info( 'Done.\n')
