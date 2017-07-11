from re import match



class IRCChannel():
    def __init__(self, channelName):
        self._name = channelName
        self._topic = ""
        self._creationTime = 0
        self._creator = ""
        self.users = IRCUserList()

    def __repr__(self): return self.getName()

    def getName(self):  return self._name
    def getTopic(self): return self._topic
    def getCreationTime(self): return self._creationTime
    def getCreator(self): return self._creator

    def setName(self, name): self._name = name
    def setTopic(self, topic): self._topic = topic
    def setCreationTime(self, creationTime): self._creationTime = creationTime
    def setCreator(self, creator): self._creator = creator

class IRCHost():
    def __init__(self, host=""):
        self._host = host
        self._regexp = "(?P<nick>[^@!\ ]*)(?:(?:!(?P<ident>[^@]*))?@(?P<host>[^\ ]*))?"

    def setFullHost(self, host):  self._host = host
    def getFullHost(self): return self._host

    def getNick(self): return match(self._regexp, self._host).group("nick")
    def getIdent(self): return match(self._regexp, self._host).group("ident")
    def getHost(self): return match(self._regexp, self._host).group("host")

    def __repr__(self): return self._host

class IRCUser(IRCHost):
    def __init__(self, host=""):
        IRCHost.__init__(self, host)

        self._voice = False
        self._hop = False
        self._op = False
        self._admin = False
        self._owner = False

        self._isbot = False
        self._isaway = False
        self._isregistered = False
        self._isircop = False

    def getMNick(self):
        prefix = ""
        if self.isOwner(): prefix = "~"
        elif self.isAdmin(): prefix = "&"
        elif self.isOp(): prefix = "@"
        elif self.isHop(): prefix = "%"
        elif self.isVoice(): prefix = "+"

        return prefix + self.getNick()

    # MODES SETTERS : LEVELS
    def setVoice(self, voice=True):  self._voice = voice
    def setHop(self, hop=True): self._hop = hop
    def setOp(self, op=True): self._op = op
    def setAdmin(self, admin=True): self._admin = admin
    def setOwner(self, owner=True): self._owner = owner
    def setAway(self, away=True): self._away = away
    def setMode(self, mode, modifier):
        if mode == "v": self.setVoice(modifier)
        elif mode == "h": self.setHop(modifier)
        elif mode == "o": self.setOp(modifier)
        elif mode == "a": self.setAdmin(modifier)
        elif mode == "q": self.setOwner(modifier)
    # MODES SETTERS : ADVANCED STATUS
    def setBot(self, isbot=True): self._isbot = isbot
    def setAway(self, isaway=True): self._isaway = isaway
    def setRegistered(self, isregistered=True): self._isregistered = isregistered
    def setIRCOp(self, isircop=True): self._isregistered = isircop


    # MODES GETTERS : LEVELS
    def isVoice(self): return self._voice
    def isHop(self): return self._hop
    def isOp(self): return self._op
    def isAdmin(self): return self._admin
    def isOwner(self): return self._owner
    # MODES GETTERS : ADVANCES STATUS
    def isBot(self): return self._isbot
    def isAway(self): return self._away
    def isRegistered(self): return self._isregistered
    def isIRCOp(self): return self._isircop

    def __repr__(self):  return self.getNick()




class IRCUserList():

    def __init__(self):
        self._internalList = list()
        #TODO : Add methods for Query Users (Eg : All Opers, owners etc ...)

    def __getitem__(self, item):
        for user in self._internalList:
            if user.getNick() == item:
                return user
        raise KeyError

    def __setitem__(self, key, value):
        self._internalList.append(value)

    def __delitem__(self, key):
        for index in range(len(self._internalList)):
            if self._internalList[index].getNick() == key:
                del self._internalList[index]
                return True

    def __iter__(self): return iter(self._internalList)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except KeyError: return False



class IRCChannelList():
    def __init__(self):
        self._internalList = list()
        #TODO : Add methods for Query Channel (Eg : All channels with 3 users, or 3 channels where Jack is in)

    def __getitem__(self, item):
        for channel in self._internalList:
            if channel.getName() == item:
                return channel
        raise KeyError

    def __setitem__(self, key, value):
        self._internalList.append(value)

    def __delitem__(self, key):
        for index in range(len(self._internalList)):
            print("CHANNELS : Looking for %s, actually  at index %s \t[index:%s='%s']" % (key, index, index, self._internalList[index].getName()))
            if self._internalList[index].getName() == key:
                print("CHANNELS : %s found at index %s" % (key, index))
                del self._internalList[index]
                return True

    def __iter__(self):
        return iter(self._internalList)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except KeyError: return False
