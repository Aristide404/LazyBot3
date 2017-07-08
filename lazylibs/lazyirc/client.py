from socket import socket
from PyQt5.QtCore import QObject, pyqtSignal
from re import match
from lazylibs.lazyirc.core import IRCChannel, IRCChannelList, IRCHost, IRCUser
# (?::(([^@!\ ]*)(?:(?:!([^@]*))?@([^\ ]*))?)\ )?([^\ ]+)


class IRCConnectionHandler(QObject):

    disconnected = pyqtSignal(object)
    connected = pyqtSignal(object)
    identified = pyqtSignal(object)

    raw = pyqtSignal(object, str)
    ping = pyqtSignal(object, str)
    privmsg = pyqtSignal(object, str, str, str)


    def __init__(self, server="", port=0):
        QObject.__init__(self)
        self.chans = IRCChannelList()
        self._regexp = "(?::(?P<source>[^ ]+) +)?(?P<query>[^ :]+)(?P<dest>(?: +[^ :]+))*(?P<coda> +:(?P<message>.*)?)?"

        self._server = server
        self._port = port

        #QTcpSocket.readyRead.connect(self._parseMessage)
        self.sk = socket()



    def openConnection(self):
        print("Connecting ...")
        self.sk.connect((self.getServer(), self.getPort()))
        self.sendData("NICK DeLaCouille")
        self.sendData("USER DeLaCouille Testiculas lazybot :Mes couilles sur ton front - je te ferais la licorne de la honte")
        data = ""
        while data != None:
            data = self.waitForData()
            print("RECEIVE : « %s » " % (data))
            parser = match(self._regexp, data)
            # Parse commands :
            query = parser.group("query")
            # QUERY
            if query == "PING":
                self.sendData("PONG %s" % parser.group("coda"))
                self.ping.emit(self, parser.group("coda"))
            elif query == "PRIVMSG":
                #self.sendData("PRIVMSG %s :Franchement, %s, ce n'est pas que je t'aimes pas. J'aimerais juste que tu crèves" % (parser.group("dest"), nick))
                self.privmsg.emit(self, parser.group("source"), parser.group("dest"), parser.group("message"))
            elif query == "JOIN":
                print(parser.group("message"))
                chan = parser.group("message").strip()
                if not chan in self.chans:
                    print("New channel :")
                    self.chans[chan] = IRCChannel(chan)
                    self.sendData("WHO %s" % (chan))
                else:
                    self.addUserInChannel(chan, parser.group("source").strip())
            elif query == "PART":
                self.delUserInChannel(parser.group("dest").strip(), parser.group("source").strip())
            elif query == "QUIT":
                for channel in self.chans:
                    self.delUserInChannel(channel, parser.group("source").strip())
            elif query == "MODE":
                #«:Aristide!Aristide@staffOP.timeia.fr MODE #Channel +o-o+v-v DeLaCouille DeLaCouille DeLaCouille DeLaCouille »
                # Must be parsed, v, h, o, a, q, b and e, need to be parsed with argument.
                chan = data.split(" ")[2]
                modeString = data.split(" ")[3]
                argList = data.split(" ")[4:]
                argListIndex = 0
                modifier = True
                for char in modeString:
                    if char == "+": modifier = True
                    elif char == "-": modifier = False
                    elif char == "v" or char == "h" or char == "o" or char == "a" or char == "q":
                        nickPointer = self.chans[chan].users[argList[argListIndex]]
                        argListIndex += 1
                        nickPointer.setMode(char, modifier)

            # NUMBERS
            elif query == "001":
                #TODO : For test !!! REMOVE ON INTIIAL RELEASE
                self.sendData("JOIN #test,#test2")
                #TODO ========================================
                self.identified.emit(self)
            elif query == "332":
                # WHEN YOU JOIN CHANNEL - TOPIC
                chan = self.chans[parser.group("dest").strip()]
                chan.setTopic(parser.group("message").strip)
            elif query == "333":
                # WHEN YOU HAVE CREATOR AND DATE
                #NOTE : This query require a special parser.
                #Channel is Index : 3
                #Author is Index : 4
                #Date is Index : 5
                chan = data.split(" ")[3]
                author = data.split(" ")[4]
                cdate = int(data.split(" ")[5])
                self.chans[chan].setCreationTime(cdate)
                self.chans[chan].setCreator(author)
            elif query == "352":
                # WHO LINE
                #« :irc.timeia.fr 352 DeLaCouille #Test Timeia Bot.Timeia.fr hidden Timeia H& :0 Timeia »
                #292  G - L'utilisateur est /away (absent)
                # 292  H - L'utilisateur est n'est pas /away (présent)
                # 292  r - L'utilisateur utilise un pseudo enregistré
                # 292  B - L'utilisateur est un bot (+B)
                # 292  * - L'utilisateur est un Opérateur IRC
                # 292  ~ - L'utilisateur est un Channel Owner (+q)
                # 292  & - L'utilisateur est un Channel Admin (+a)
                # 292  @ - L'utilisateur est un Channel Operator (+o)
                # 292  % - L'utilisateur est un Halfop (+h)
                # 292  + - L'utilisateur est Voicé (+v)
                # 292  ! - L'utilisateur est +H et vous êtes un IRC Operator
                #Channel is index 3
                #Nickname is index 7
                chan = data.split(" ")[3]
                nickname = data.split(" ")[7]
                ident = data.split(" ")[4]
                host = data.split(" ")[5]
                modes = data.split(" ")[8]
                user = self.addUserInChannel(chan, "%s!%s@%s" % (nickname, ident, host))
                user.setVoice("+" in modes)
                user.setHop("%" in modes)
                user.setOp("@" in modes)
                user.setAdmin("&" in modes)
                user.setOwner("~" in modes)
                user.setBot("B" in modes)
                user.setRegistered("r" in modes)


    def closeConnection(self):
        self.sk.close()

    def waitForData(self):
        wholeData = ""
        data = ""
        while data != chr(10):
            content = self.sk.recv(1)
            try:
                data = content.decode("utf-8")
            except UnicodeDecodeError:
                data = content.decode("latin1")
            wholeData = wholeData + data

        return wholeData.strip()

    def sendData(self, data):
        print("SEND : « %s »" % (data))
        data = data + "\n"
        self.sk.send(data.encode())

    def getPort(self): return self._port
    def getServer(self): return self._server

    def setPort(self, port): self._port = port
    def setServer(self, server): self._server = server

    def addUserInChannel(self, chanName, host):
        user = IRCUser(host)
        if not user.getNick() in self.chans[chanName].users:
            self.chans[chanName].users[user.getNick()] = user
        return self.chans[chanName].users[user.getNick()]


    def delUserInChannel(self, chanName, host):
        user = IRCUser(host)
        if user.getNick() in self.chans[chanName].users:
            del self.chans[chanName].users[user.getNick()]
            return True
        else:
            return False

    def sJoin(self, chanName):
        self.sendData("JOIN %s\n" % (chanName))
    def sPart(self, chanName, reason=""):
        self.sendData("PART %s :%s\n" % (chanName, reason))
    def sPong(self, dest, content):
        self.sendData("PONG %s :%s" % (dest, content))
    def sMessage(self, dest, message):
        self.sendData("PRIVMSG %s :%s" % (dest, message))
    def sNotice(self, dest, message):
        self.sendData("NOTICE %s :%s" % (dest, message))
