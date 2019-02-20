# bc_pos
A blockchain testbed to evaluate PoS consensus

**Dependencies:**

- Python 2.7.x
- pyzmq
- configparser
---
## How to Install
Execute file install.sh as root

## How to Use

### Use in a host
1. Run in console a node
`.\node [-i <ip> -p <port>]`
2. Run in another console a blockchain-cli
`.\blockchain-cli [parameters]`


### Use with mininet
Run `sudo python simpleNet.py [-n <quantity>]`
This file is a simple single switch Mininet topology that runs `node.py` in each host with private directories.

---

## Parameters

### simpleNet.py
`
**Arguments:**

- `-n`\
number of hosts on switch

### node

Process to run in each host participating in the network.

**Arguments:**

- `-i`  `--ip`\
IP address of the node in the network (defaults to loopback)
- `-p`  `--port`\
port to listen to peers (defaults to 9000)
- `--peers`\
list of peers IP addresses
- `--miner`\
start node mining
- `--log`\
console log level
- `-c`\
configuration file
- `-h` `--help`\
help

### blockchain-cli

Localhost client to communicate with the node process and obtain blockchain info

**Arguments:**

- `getlastblock`\
last block on the chain
- `addpeer X`\
add X peer IP and connect to it
- `removepeer X`\
remove X peer and disconnect
- `getblock X`\
block X information
- `getblocks X Y`\
blocks X and Y information
- `getpeerinfo`
IP of all connected peers
- `startmining`\
start mining on the node
- `stopmining`\
stop mining on the node
- `addbalance X`\
add X coins to balance
- `addblock X Y`\
add block with index X and round Y
- `exit`\
stop node process
- `-h` `--help`\
help
