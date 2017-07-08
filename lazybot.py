from PyQt5 import QtCore
import sys
from lazylibs.lazyirc.client import IRCConnectionHandler
from lazylibs.lazyirc.core import IRCChannel, IRCChannelList
print("LazyBot 3.0.1 - IRC Bot for IRC ...")
print("Initializing core component")
app = QtCore.QCoreApplication(sys.argv)

client = IRCConnectionHandler()
client.setServer("<test>")
client.setPort(6667)
client.openConnection()

exit(app.exec_())

