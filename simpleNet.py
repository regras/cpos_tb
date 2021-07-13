from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info

from functools import partial
from time import sleep
from random import shuffle
import numpy
import sys, os
import time
import random
import parameter
import math
import hashlib
# Sample usage
# sudo python simpleNet.py <n>
# n: number of hosts

# file directory path to mount private dirs
dir_path = os.path.dirname(os.path.realpath(__file__))

def testHostWithPrivateDirs(number=5):
    "Test bind mounts"
    topo = SingleSwitchTopo( number )
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    #startServer(net,number)
    CLI( net )
    stopServer(net.hosts)
    net.stop()

def startServer(net,number):
    stake = parameter.numStake
    print(stake)
    """ Start node.py process passing all hosts ip addresses """
    j = 1
    for h in net.hosts:
        stakeNode = []
        node = hashlib.sha256(str(h.IP())).hexdigest()            
        for i in stake:
            #stakeNode = stakeNode + stake[i][j]
            stakeNode = stakeNode + stake[i][node]

        o = net.hosts[:]
        o.remove(h)
        ips = [x.IP() for x in o]
        stakeNode = [str(x) for x in stakeNode]
        shuffle(ips)
        peers = ' '.join(ips)
        stakeNode = ' '.join(stakeNode)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('nohup python node.py -i', h.IP(), '-p 9000 --stake %s &' %(stakeNode))
        #time.sleep(2)
        #if(j == 1):
        #    h.cmd('sudo nohup python transaction.py &')
        j = j + 1

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
