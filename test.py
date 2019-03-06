from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info

from functools import partial
import sys, os

import parameter
import sqldb
from timeit import default_timer as timer
from random import shuffle

dir_path = os.path.dirname(os.path.realpath(__file__))

def timetocreateblocks():
    topo = SingleSwitchTopo(parameter.test_num_nodes)
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    peers = []
    net.start()
    for h in net.hosts:
        o = net.hosts[:]
        o.remove(h)
        ips = [x.IP() for x in o]
        shuffle(ips)
        peers = ' '.join(ips)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('python node.py -i', h.IP(), '-p 9000 --peers %s &' % peers)
    #startServer(net)
    start = timer()
    end = timer()
    count = 1
    locked = False
    while count < 11:
        start = timer()
        if not locked:
            for h in net.hosts:
                h.cmd('rpc/rpcclient.py startmining')
            locked = True
        
        if sqldb.getLastBlockIndex() == 3:
            for h in net.hosts:    
                h.cmd('rpc/rpcclient.py stopmining')
            end = timer()
            info('Para um' ,parameter.timeout, end - start)
            locked = False
            count = count + 1
    #CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    timetocreateblocks()
