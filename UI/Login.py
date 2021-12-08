import tkinter as tk
from tkinter import StringVar, ttk
import hashlib

hypothetical_credentials_from_database = {
  'user' : hashlib.sha256("pass".encode('utf-8')).hexdigest(),
  'user2' : hashlib.sha256("pass2".encode('utf-8')).hexdigest(),
  'user3' : hashlib.sha256("pass3".encode('utf-8')).hexdigest()}

# UI
class Login():
  def __init__(self):
    self.failures = 0
    self.root = tk.Tk()
    self.root.title("BasedCoin")
    self.root.grid_rowconfigure(0, weight=1)
    self.root.grid_columnconfigure(0, weight=1)
    credentialFrame = tk.Frame(self.root)
    self.uname = StringVar()
    self.pwd = StringVar()
    self.errorVar = StringVar()
    self.loggedIn = False
    self.credentials = str()

    tk.Label(self.root, text="BasedCoin Login", font=('', 18, 'bold')).grid(row=0, column=0, sticky='EW', pady=8)
    errorLabel = tk.Label(self.root, textvariable=self.errorVar, fg='#ff0000')
    errorLabel.grid(row=1, column=0, sticky='EW')

    credentialFrame.grid(row=2, column=0, sticky='')
    tk.Label(credentialFrame, text="Username").grid(row=0, column=0)
    tk.Entry(credentialFrame, width=20, textvariable=self.uname).grid(row=0, column=1)
    tk.Label(credentialFrame, text="Password").grid(row=1, column=0)
    tk.Entry(credentialFrame, show='\u2022', width=20, textvariable=self.pwd).grid(row=1, column=1)

    tk.Button(self.root, text="Login", command=self.doLogin, width=10).grid(row=3, column=0, sticky='', pady=8)

    # Login with enter key
    self.root.bind('<Return>', self.doLogin)
    self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
    self.root.mainloop()

  # Hashes password and checks if it matches a user:pass pair
  def doLogin(self, *args):
    #print("Received credentials:", self.uname.get(), hashlib.sha256(self.pwd.get().encode('utf-8')).hexdigest())
    if self.checkCredentials():
      self.errorVar.set('')
      self.closeAppOnSuccess()
    else:
      self.failures += 1
      self.errorVar.set("Incorrect credentials")
      if self.failures > 3:
        self.root.destroy()
  
  # Does the checking
  def checkCredentials(self):
    if self.uname.get().lower() in hypothetical_credentials_from_database:
      if hashlib.sha256(self.pwd.get().encode('utf-8')).hexdigest() == hypothetical_credentials_from_database[self.uname.get().lower()]:
        #print("Correct")
        self.credentials = self.uname.get().lower()
        self.uname.set('')
        self.pwd.set('')
        return True
      else:
        self.pwd.set('')
        return False
    else:
      self.pwd.set('')
      return False
  
  # Opens wallet interface
  def closeAppOnSuccess(self):
    self.root.destroy()
    self.loggedIn = True

  def getCredentialsFromDatabase(self):
    # Do some stuff with SQL and return a list object with username and password
    pass

# Uncomment this if NOT running with Main.py
#Login()