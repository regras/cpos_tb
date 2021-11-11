#!/bin/bash
service ssh start &
/etc/init.d/mysql start &
#screen -d -m python node.py -i $(ifdata -pa eth0) -p 9000 
nohup python node.py -i $(ifdata -pa eth0) -p 9000 > file &
/bin/bash
