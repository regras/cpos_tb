#!/bin/bash
screen -d -m python node.py -i $(ifdata -pa eth0) -p 9000 &
service ssh start
/bin/bash
