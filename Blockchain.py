# Nick Alvarez
# Olliver Aikenhead
# CS 491.1003, Fall 2021
# Project

# Blockchain module/classes file

import datetime
import hashlib
import random

class Block:
  blockNo = 0
  data = None
  next = None
  nonce = 0
  previous_hash = 0x0
  timestamp = datetime.datetime.now()

  def __init__(self, data):
    self.data = data
    self.hashVar = None
    if self.blockNo == 0:
      self.hash() # Genesis block

  def hash(self):
    h = hashlib.sha256()
    h.update(
    str(self.nonce).encode('utf-8') +
    str(self.data).encode('utf-8') +
    str(self.previous_hash).encode('utf-8') +
    str(self.timestamp).encode('utf-8') +
    str(self.blockNo).encode('utf-8')
    )
    self.hashVar = h.hexdigest()
    return self.hashVar
  
  # prints blockchain vars to terminal
  def __str__(self):
    return "Block Hash: " + str(self.hashVar) + "\nBlockNo: " + str(self.blockNo) + "\nBlock Data: " + str(self.data) + "\nHashes: " + str(self.nonce) + "\nPrev. Hash: " + str(self.previous_hash) + "\nTimestamp: " + str(self.timestamp) + "\n--------------"

class Blockchain:
  # difficulty for the miner to guess a nonce that matches this hash
  #diff = 20
  #maxNonce = 2**32
  #target = 2 ** (256-diff)
  difficulty_hash = 0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

  # Initial block creation
  block = Block("Genesis")
  dummy = head = block

  # Moving pointer
  def add(self, block):

    block.previous_hash = self.block.hashVar
    block.blockNo = self.block.blockNo + 1

    self.block.next = block
    self.block = self.block.next

  # Mining, incrementing nonce
  def mine(self, block):
    #for n in range(self.maxNonce):
    while int(int(block.hash(), 16) >= self.difficulty_hash):
      #if int(block.hash(), 16) <= self.target:
      #  self.add(block)
      #  print(block)
      #  break
      #else:
      #print(block.hashVar)
      block.nonce += 1
    self.add(block)
    return block

class MerkleLeaf:
  def __init__(self, val):
    self.data = val
    h = hashlib.sha256()
    h.update(str(self.data).encode('utf-8'))
    self.hash = h.hexdigest()

class MerkleTree:
  
  def __init__(self, users, size):
    self.users = users
    self.tree = list()
    self.transactions = list()
    self.nodesLevelAbove = list()

    for i in range(size):
      self.createRandomTransaction()
    self.addTransactionHashes()
    while size>0:
      self.makeNodeHashes(size)
      size = int(size/2)
      if size>1:
        size = (size + 1) if (size % 2) else size # Odd number of nodes

    self.rootHash = self.tree[0]

  def createNode(self, data):
    return MerkleLeaf(data)
  
  def addTransactionHashes(self):
    for data in self.transactions:
      self.tree.insert(0, data.data)
    for hash in self.transactions:
      self.tree.insert(0, hash.hash)
  
  def makeNodeHashes(self, nodes):
    
    def createNodeAbove(start, finish):
      hashes = ""
      for hash in range(start, finish):
        hashes += self.tree[hash]
      return self.createNode(hashes)

    if (int(nodes/2)):
      for i in range(int(nodes/2)):
        node = createNodeAbove(i*2, (i*2)+2)
        self.nodesLevelAbove.append(node.hash)
      for hash in self.nodesLevelAbove:
        self.tree.insert(self.nodesLevelAbove.index(hash), hash)
      self.nodesLevelAbove.clear()

  def createRandomTransaction(self):
    fromUser = self.users[random.randint(0, (len(self.users)-1))]
    toUser = self.users[random.randint(0, (len(self.users)-1))]
    while toUser == fromUser:
      toUser = self.users[random.randint(0, (len(self.users)-1))]
    
    data = {
      'from': fromUser, # From and To would actually be bitcoin addresses
      'to': toUser,
      'amount': random.randint(1,100)
    }
    node = self.createNode(data)
    self.transactions.insert(0, node)
  

  # Function for call from Wallet interface
  def createTransaction(self, fromUser, toUser, amount, reason=''):
    if fromUser == toUser:
      return False

    data = {
      'from': fromUser, # From and To would actually be bitcoin addresses
      'to': toUser,
      'amount': amount
    }
    node = self.createNode(data)
    self.transactions.insert(0, node)