import socket, pickle, base64, copy
from Blockchain import Block, Blockchain

def server_program():
  host = socket.gethostname()
  port = 5000

  server_socket = socket.socket()
  server_socket.bind((host, port))
  server_socket.listen(10)

  pendingTransactions = dict()
  b = Blockchain()

  def retrieveTransactions(a):
    try:
      return pendingTransactions.pop(a)
    except KeyError:
      return 0

  def getTheChain():
    tempList = list()
    tempPtr = copy.deepcopy(b.head)
    while tempPtr != None:
      tempList.append(tempPtr.hashVar)
      tempPtr = tempPtr.next
    return tempList

  def acceptMessage():
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    while True:
      try:
        data = conn.recv(1024)
        data_obj = pickle.loads(base64.b64decode(data))
        if not data:
          # Data is not received
          break
        print("from connected user: " + str(data_obj))
        if data_obj[0] == "Block":
          out = b.mine(Block(data_obj))
          try:
            pendingTransactions[(data_obj[1])["to"]] += (data_obj[1])["amount"]
          except KeyError:
            pendingTransactions[(data_obj[1])["to"]] = (data_obj[1])["amount"]
        elif data_obj[0] == "Request":
          out = getTheChain()
        elif data_obj[0] == "Update":
          out = retrieveTransactions(data_obj[1])
        else:
          break
        conn.send(base64.b64encode(pickle.dumps(out)))
        
      except EOFError:
        conn.close()
        break
      except ConnectionResetError:
        conn.close()
        break
  
  while True:
    acceptMessage()


if __name__ == '__main__':
  server_program()