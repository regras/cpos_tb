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
        #print(o)
        o.remove(h)
        ips = [x.IP() for x in o]
        shuffle(ips)
        peers = ' '.join(ips)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('python node.py -i', h.IP(), '-p 9000 --miner --peers %s &' % peers)

    
        if(h.IP() == '10.0.0.1'):
            #h.cmd('python uni_test.py')
            host = h 
        #startServer(net)
        # info('*** Creating 100 blocks ***\n')
        # start = timer()
        # end = timer()
        # count = 1
        # locked = False
        # while count < 2:
        #     start = timer()
        #     if not locked:
        #         for h in net.hosts:
        #             info('*** Blockchain node  %s start mining\n' % h)
        #             h.cmd('rpc/rpcclient.py startmining')
        #         locked = True
            
        #     if sqldb.getLastBlockIndex() == 100:
        #         for h in net.hosts:
        #             info('*** Blockchain node  %s stop mining\n' % h)
        #             h.cmd('rpc/rpcclient.py stopmining')
        #         end = timer()
        #         info('Para um' ,parameter.timeout, end - start)
        #         locked = False
        #         count = count + 1
        # for h in net.hosts:
        #    info('*** Creating 100 blocks in %s ***\n' % h)
        #    h.cmd('python uni_test.py')
    net.get('h1').cmd('python uni_test.py &')
    CLI( net )    
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    timetocreateblocks()
