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

dir_path = os.path.dirname(os.path.realpath(__file__))

def timetocreateblocks():
    topo = SingleSwitchTopo(parameter.TEST_NUM_NODES)
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    peers = []
    net.start()
    for h in net.hosts:
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('rm /tmp/%(name)s/blocks/blockchain.db')
        h.cmd('python node.py -i', h.IP(), '-p 9000 --peers %s &' % peers)
    #startServer(net)
    parameter.timeout = 0.5
    start = timer()
    end = timer()
    while parameter.timeout < 60:
        start = timer()
        for h in net.hosts:
            h.cmd('rpc/rpcclient.py startmining')
        
        if sqldb.getLastBlockIndex() == 3:
            for h in net.hosts:    
                h.cmd('rpc/rpcclient.py stopmining')
            end = timer()
            info('Para um' ,parameter.timeout, end - start)
            parameter.timeout = parameter.timeout + 1
    #CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    timetocreateblocks()
