from UI import Login, Wallet
import sys

# Ask for credentials
loginWindow = Login.Login()
if loginWindow.loggedIn: # If authentication successful, open wallet
  Wallet.Interface(loginWindow.credentials)
else:
  sys.exit()