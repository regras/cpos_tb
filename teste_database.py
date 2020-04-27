import sqlite3
import logging
import block
import blockchain
import leaf
import leafchain
import parameter
from collections import deque, Mapping, defaultdict
import pickle
logger = logging.getLogger(__name__)
databaseLocation = 'blocks/blockchain.db'
