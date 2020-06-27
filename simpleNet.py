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
def testHostWithPrivateDirs(number=2):
    "Test bind mounts"
    topo = SingleSwitchTopo( number )
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    startServer(net,number)
    CLI( net )
    stopServer(net.hosts)
    net.stop()

def startServer(net,number):
    stake = parameter.defineStake(number)
    print(stake)
    """ Start node.py process passing all hosts ip addresses """
    j = 1
    for h in net.hosts:
            stakeNode = []
            for i in stake:
                stakeNode = stakeNode + stake[i][j]
            o = net.hosts[:]
            o.remove(h)
            ips = [x.IP() for x in o]
            stakeNode = [str(x) for x in stakeNode]
            shuffle(ips)
            peers = ' '.join(ips)
            stakeNode = ' '.join(stakeNode)
            print(peers)
            print(stakeNode)            
            info('*** Blockchain node starting on %s\n' % h)
            #if(h.IP() == '10.0.0.1'):
            h.cmd('nohup python node.py -i', h.IP(), '-p 9000 --s %s --peers %s &' %(stakeNode, peers))
            #else:
            #    h.cmd('python node.py -i', h.IP(), '-p 9000 --s %s --peers %s &' %(stakeNode, peers))
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
