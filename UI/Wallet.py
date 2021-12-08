import tkinter as tk
from tkinter.constants import END
import tkinter.messagebox as mb
import tkinter.filedialog as fd
from tkinter import StringVar, ttk
from UI.Capture import Capturing
from Blockchain import Block, Blockchain
import os
import copy
import random
import datetime
import hashlib
import socket
import pickle
import base64

defaultbg = ""

# This class holds the "globals" for the interface
# and provides a way to add blocks to the chain
# or check what's on the chain
class UserInfoAndHelper:
  def __init__(self):
    # Random address
    h1 = hashlib.sha256()
    h1.update(str(datetime.datetime.now()).encode('utf-8'))
    self.address = str(h1.hexdigest())
    
    # Random balance
    self.availableCoin = (random.randrange(1, 100) + ((random.randrange(2,9998) / random.randrange(1, 9999))/100.0))

    # "Globals"
    self.chainHashes = list()
    self.client_socket = socket.socket()
  
  # Connection to outside world
  def connect(self):
    host = socket.gethostname()
    port = 5000
    self.client_socket = socket.socket()
    self.client_socket.connect((host, port))
  
  # Messages to server
  def sendMessage(self, t, m=''):
    self.connect()
    message = base64.b64encode(pickle.dumps([t, m]))

    self.client_socket.send(message)

    try:
      data = self.client_socket.recv(1024)
      self.client_socket.close()
      return pickle.loads(base64.b64decode(data))
    except EOFError:
      mb.showerror(title="BasedCoin", message="Something went horribly wrong. Good luck figuring it out.")
      exit()

  # Unused - single user implementation
  def addToChain_singleUser(self, data):
    result = self.chain.mine(Block(data))
    mb.showinfo(title="BasedCoin", message=f"Mined block with hash {str(result.hashVar)[:10]}... with nonce of {str(result.nonce)}")
    try:
      mb.showinfo(title="BasedCoin", message=f"Previous Hash: {str(result.previous_hash)[:10]}...")
    except:
      pass
    self.getTheChain()
  
  # Adds block to chain and displays info
  def addToChain(self, data):
    result = self.sendMessage("Block", data)
    mb.showinfo(title="BasedCoin", message=f"Mined block with hash {str(result.hashVar)[:10]}... with nonce of {str(result.nonce)}")
    try:
      mb.showinfo(title="BasedCoin", message=f"Previous Hash: {str(result.previous_hash)[:10]}...")
    except:
      pass
  
  # Returns list of blocks
  def getTheChain(self):
    self.chainHashes = self.sendMessage("Request")
  
  # Checks for pending transactions (receiving money)
  def updateCurrency(self):
    self.availableCoin += float(self.sendMessage("Update", self.address))
  
  # Unused - single user implementation
  def getTheChain_singleUser(self):
    tempList = list()
    tempPtr = copy.deepcopy(self.chain.head)
    while tempPtr != None:
      tempList.append(tempPtr.hashVar)
      tempPtr = tempPtr.next
    self.chainHashes = tempList

info = UserInfoAndHelper()

# Controller for UI
class Interface(UserInfoAndHelper):
  def __init__(self, user="Testing me aren't you"):
    global defaultbg
    self.root = tk.Tk()
    self.root.title("BasedCoin")
    self.root.grid_rowconfigure(0, weight=1)
    self.root.grid_columnconfigure(0, weight=1)
    defaultbg = self.root.cget('bg')

    # Tabs at top of window
    tabStyle = ttk.Style()
    tabStyle.theme_create("Tab Style", parent="alt", settings={
      "TNotebook": {"configure": {"background" : "white smoke",
      "foreground": "black"}},
      "TNotebook.Tab": {"configure": {"padding": [10],
      "background" : "white smoke",
      "foreground": "black"}}
    })
    tabStyle.theme_use("Tab Style")
    self.tabControl = ttk.Notebook(self.root)

    self.wallet = WalletTab(self.tabControl)
    self.send = SendTab(self.tabControl)
    self.blockchain = BlockchainTab(self.tabControl)
    self.contracts = ContractsTab(self.tabControl)
    self.settings = SettingsTab(self.tabControl)

    self.tabControl.add(self.wallet, text="Wallet")
    self.tabControl.add(self.send, text="Send")
    self.tabControl.add(self.blockchain, text="Blockchain")
    self.tabControl.add(self.contracts, text="Contracts")
    self.tabControl.add(self.settings, text="Settings")
    self.tabControl.grid(row=0, column=0, sticky='new')

    tk.Label(self.root, text=f"Logged in as {user}", bd=1, relief=tk.SUNKEN, anchor=tk.W).grid(sticky='sew')

    def closeMe():
      info.client_socket.close()
      self.root.destroy()

    self.root.protocol("WM_DELETE_WINDOW", closeMe)
    self.root.mainloop()
  
# Wallet Tab
class WalletTab(tk.Frame, UserInfoAndHelper):
  def __init__(self, master):
    super().__init__(master)
    self.grid_columnconfigure(0, weight=1)
    addressFrame = tk.Frame(self)
    tk.Label(self, text="Wallet Overview", font=('', 18, 'bold')).grid(row=0, column=0, sticky='w')
    self.currentAvailableCoin = StringVar()
    self.currentAvailableCoin.set(f"Current balance: {info.availableCoin} BSD")

    def on_visibility(event=None):
      info.updateCurrency()
      self.currentAvailableCoin.set(f"Current balance: {info.availableCoin} BSD")
      self.update()

    addressFrame.grid(row=1, column=0)
    tk.Label(addressFrame, text="Your wallet address is: ").grid(row=0, column=0)
    walletAddress = tk.Text(addressFrame, height=1, borderwidth=0, background=defaultbg)
    walletAddress.insert(1.0, info.address)
    walletAddress.configure(state="disabled")
    walletAddress.config(width=len(info.address))
    walletAddress.grid(row=0, column=1)
    tk.Label(self, textvariable=self.currentAvailableCoin).grid(row=2, column=0)
    tk.Button(self, text="Update", width=10, command=on_visibility).grid(row=3, column=0)

    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)
    
    # When navigating to page, check for balance updates
    self.bind("<Visibility>", on_visibility)

# Send Tab
class SendTab(tk.Frame, UserInfoAndHelper):
  def __init__(self, master):
    super().__init__(master)
    self.receiver = tk.StringVar()
    self.amount = tk.StringVar()
    self.reason = tk.StringVar()

    tk.Label(self, text="Send Money", font=('', 18, 'bold')).grid(row=0, column=0, sticky='w')

    # Input validation
    def submitHelper():
      tempReceiver = self.receiver.get()
      tempAmount = self.amount.get()
      tempReason = self.reason.get()

      if tempReceiver != '':
        try:
          tempAmount = float(tempAmount)
          if tempAmount > 0.0:
            if info.availableCoin-tempAmount > 0.0:
              self.receiver.set('')
              self.reason.set('')
              self.amount.set('')

              tempData = {
                'from' : info.address,
                'to' : tempReceiver,
                'amount': tempAmount,
                'reason' : tempReason
              }

              info.availableCoin -= tempData['amount']
              info.addToChain(tempData)
            else:
              mb.showerror(title="BasedCoin", message="You do not have enough BasedCoin to perform this transaction!")
          else:
            mb.showerror(title="BasedCoin", message="Amount to send must be greater than zero.")
        except ValueError:
          mb.showerror(title="BasedCoin", message="Amount to send must be a positive number.")
      else:
        mb.showerror(title="BasedCoin", message="There must be a valid recipient address.")

    recipientFrame = tk.Frame(self)
    recipientFrame.grid(row=1, column=0)
    tk.Label(recipientFrame, text="Receiver Address").grid(row=0, column=0)
    tk.Entry(recipientFrame, width=20, textvariable=self.receiver).grid(row=0, column=1)
    tk.Label(recipientFrame, text="Amount").grid(row=1, column=0)
    tk.Entry(recipientFrame, width=20, textvariable=self.amount).grid(row=1, column=1)
    tk.Label(recipientFrame, text="Reason (optional)").grid(row=2, column=0)
    tk.Entry(recipientFrame, width=20, textvariable=self.reason).grid(row=2, column=1)

    tk.Button(self, text="Send", width=10, command=submitHelper).grid(row=2, column=0, columnspan=2, sticky='')

    # Pressing enter will send money
    self.bind('<Return>', submitHelper)

    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)

# Blockchain Tab
class BlockchainTab(tk.Frame, UserInfoAndHelper):
  def __init__(self, master):
    super().__init__(master)
    self.currentHash = 0
    self.leftLabel = StringVar()
    self.leftHash = StringVar()
    self.centerLabel = StringVar()
    self.centerHash = StringVar()
    self.rightLabel = StringVar()
    self.rightHash = StringVar()
    
    self.leftLabel.set('')
    self.centerLabel.set('')
    self.rightLabel.set('')
    self.leftHash.set('')
    self.centerHash.set('')
    self.rightHash.set('')

    tk.Label(self, text="View the Blockchain", font=('', 18, 'bold')).grid(row=0, column=0, sticky='w')

    # Updates value of block no. and hash
    def setLabelState(t, s, i):
      labelText = ''
      hashText = ''
      if (s-i) > s:
        pass
      elif s > 0:
        labelText = f"Block {s-i}"
        hashText = f"{str(info.chainHashes[s-i])[:10]}..."

      t[0].set(labelText)
      t[1].set(hashText)

    # "Navigates" through chain
    def setLabel():
      i = self.currentHash
      blockIndex = len(info.chainHashes)-1
      setLabelState([self.leftLabel, self.leftHash], blockIndex, i+1)
      setLabelState([self.centerLabel, self.centerHash], blockIndex, i)
      setLabelState([self.rightLabel, self.rightHash], blockIndex, i-1)

    def moveLeft():
      if len(info.chainHashes)-2-self.currentHash > 0:
        self.currentHash += 1
        setLabel()
    
    def moveRight():
      if self.currentHash > 0:
        self.currentHash -= 1
        setLabel()
    
    setLabel()

    blockchainFrame = tk.Frame(self)
    blockchainFrame.grid(row=1, column=0)
    tk.Label(blockchainFrame, textvariable=self.leftLabel, font=('', 12, 'bold')).grid(row=0, column=0)
    tk.Label(blockchainFrame, textvariable=self.leftHash).grid(row=1, column=0)
    tk.Label(blockchainFrame, textvariable=self.centerLabel, font=('', 12, 'bold')).grid(row=0, column=1)
    tk.Label(blockchainFrame, textvariable=self.centerHash).grid(row=1, column=1)
    tk.Label(blockchainFrame, textvariable=self.rightLabel, font=('', 12, 'bold')).grid(row=0, column=2)
    tk.Label(blockchainFrame, textvariable=self.rightHash).grid(row=1, column=2)

    tk.Button(blockchainFrame, text="<", command=moveLeft).grid(row=2, column=0, sticky='w')
    tk.Button(blockchainFrame, text=">", command=moveRight).grid(row=2, column=2, sticky='e')
    
    def on_visibility(event=None):
      info.getTheChain()
      setLabel()
      self.update()

    tk.Button(self, text="Refresh", width=10, command=on_visibility).grid(row=2, column=0)
    
    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)
    
    for child in blockchainFrame.winfo_children():
      child.grid_configure(padx=12, pady=2)
    
    # Check for blockchain updates when opening tab
    self.bind("<Visibility>", on_visibility)

# Contracts tab
class ContractsTab(tk.Frame, UserInfoAndHelper):
  def __init__(self, master):
    super().__init__(master)
    self.filepath = str()
    self.filename = StringVar()
    self.activecontract = str()
    self.ctOut = list()
    tk.Label(self, text="Set Contracts", font=('', 18, 'bold')).grid(row=0, column=0, sticky='w')
    ctFrame = tk.Frame(self)

    # Gets filename from user
    def fileHelper():
      self.filepath = fd.askopenfilename(filetypes=[("Python Files", "*.py")])
      if self.filepath != '':
        if os.name == 'posix':
          self.filename.set(self.filepath.split("/")[-1:])
        elif os.name == 'nt':
          self.filename.set(self.filepath.split("/")[-1:])
        self.nameLabel.config(font=('', 12, 'normal'))
    
    # Allows the file to be executed
    def markFileActive():
      self.activecontract = self.filepath
      self.nameLabel.config(font=('', 12, 'bold'))
    
    def markFileInactive():
      self.activecontract = str()
      self.nameLabel.config(font=('', 12, 'normal'))

    # Use some currency to execute a contract
    def doExecute():
      if self.activecontract != '':
        tempData = {
          'from' : info.address,
          'to' : '',
          'amount' : random.randrange(1, 1000)/1000.0,
          'reason' : f"Execution of {self.activecontract}"
        }
        info.availableCoin -= tempData['amount']
        info.addToChain(tempData)
        with Capturing() as output:
          exec(open(self.activecontract).read())
        self.ctOut.clear()
        self.ctOut = output
        self.consoleOut.delete(1.0, self.consoleOut.index(END))
        for line in self.ctOut:
          self.consoleOut.insert(END, f"{line}\n")
      else:
        mb.showwarning(title="BasedCoin", message="No contract selected!")
        self.consoleOut.delete(1.0, self.consoleOut.index(END))

    ctFrame.grid(row=1, column=0, sticky='ew')
    leftCtFrame = tk.Frame(ctFrame)
    rightCtFrame = tk.Frame(ctFrame)

    leftCtFrame.grid(row=0, column=0, sticky='nw')
    tk.Label(leftCtFrame, text="Management", font=('', 14, 'bold')).grid(row=0, column=0, pady=[0, 8])
    tk.Button(leftCtFrame, text="Choose Contract", command=fileHelper).grid(row=1, column=0)
    self.nameLabel = tk.Label(leftCtFrame, textvariable=self.filename)
    self.nameLabel.grid(row=2, column=0, pady=[0, 12])
    tk.Button(leftCtFrame, text="Apply", command=markFileActive).grid(row=3, column=0)
    tk.Button(leftCtFrame, text="Disable", command=markFileInactive).grid(row=4, column=0)

    tk.Label(ctFrame).grid(row=0, column=1, padx=24)

    rightCtFrame.grid(row=0, column=2, sticky='ne')
    tk.Label(rightCtFrame, text="Control", font=('', 14, 'bold')).grid(row=0, column=0, pady=[0,8])
    tk.Button(rightCtFrame, text="Execute", command=doExecute).grid(row=1, column=0)
    self.consoleOut = tk.Text(rightCtFrame, height=8, borderwidth=1, width=40)
    self.consoleOut.grid(row=2, column=0)
    self.consoleOut.bind("<Key>", lambda e: "break")

    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)

# Settings Tab
class SettingsTab(tk.Frame, UserInfoAndHelper):
  def __init__(self, master):
    super().__init__(master)
    self.blueStatus = tk.IntVar()
    self.bgcolor = defaultbg
    tk.Label(self, text="Change Settings", font=('', 18, 'bold')).grid(row=0, column=0, sticky='w')
    tk.Checkbutton(self, text="Blue", command=self.setBlue, variable=self.blueStatus, onvalue=1, offvalue=0).grid(row=1, column=0, sticky='w')

    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)
  
  def setBlue(self):
    global defaultbg
    if self.blueStatus.get() == 1:
      self.config(background="cyan")
      self.bgcolor = "cyan"
    elif self.blueStatus.get() == 0:
      self.config(background=defaultbg)
      self.bgcolor = defaultbg
    for child in self.winfo_children():
      child.config(bg=self.bgcolor)
    self.update()

    for child in self.winfo_children():
      child.grid_configure(padx=12, pady=2)

# Uncomment this if NOT running with Main.py
#Interface()