# coding: utf8

# irc.py
# created: 2015-06-04 09:38:35
# Copyright @ 2015 breaker <breaker@broken.su>

__version__ = '0.1a'
__author__ = 'breaker <breaker@broken.su>'
__date__ = '2015-06-04'

import socket
import re
import commands as cmd
import errors as err
from twisted.internet import protocol, reactor, defer
from time import time


class Client(protocol.Protocol, cmd.commandMixin):

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, name):
        valid_nickname = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9-]{0,9}$")
        if valid_nickname.match(name):
            if name not in self.server.clients.keys() or self.server.clients[name] == self:
                if self.nickname in self.server.clients.keys():
                    self.server.clients.pop(self.nickname)
                    for chan in self.channels.keys():
                        self.channels[chan].clients.pop[self.nickname]
                        self.channels[chan].clients[name] = self
                        if self.nickname in self.channels[chan].invites:
                            self.channels[chan].invites.remove(self.nickname)
                            self.channels[chan].invites.append(name)
                        self.names_cmd([chan])
                self.server.clients[name] = self
                self._nickname = name
            else:
                raise AssertionError("Nick name is already in use!")
        else:
            raise ValueError("Erroneous nickname")

    @property
    def realm(self):
        return "%s!%s@%s" % (self.nickname, self.nickname, self.hostname)

    def ping(self):
        if (time()-self.lastaction) > 30:
            d=self.sendLine("%s PING %s" % (self.realm, str(id(self))))
            d.addCallback(self.sentDone)
            d.addErrback(self.quit_cmd)
        reactor.callLater(60, self.ping)

    def connectionMade(self):
        self.server = self.factory
        self._nickname = 'user'+str(id(self))[-5:]
        self.away = None
        self.realname = ''
        self.servername = self.server.name
        self.password = None
        self.channels = {}
        self.registered = False
        self.i = False
        self.s = False
        self.w = False
        self.o = False
        self.lastaction = 0
        self.hostname = socket.gethostname()
        self.ping()
        print "Client from %s is coming" % self.hostname

    def connectionLost(self, reason):
        self.sendToChan(self.channels.values(), "QUIT", str(reason.value))
        for channel in self.channels.keys():
            self.channels[channel].clients.pop(self.nickname)
            if self.nickname in self.channels[channel].invites:
                self.channels[channel].invites.remove(self.nickname)
            if self.nickname in self.channels[channel].o:
                self.channels[channel].o.remove(self.nickname)
            if self.nickname in self.channels[channel].v:
                self.channels[channel].v.remove(self.nickname)
            self.channels.pop(channel)
        if self.nickname in self.server.operators.keys():
            self.server.operators.pop(self.nickname)
        if self.nickname:
            self.server.clients.pop(self.nickname)
        del self

    def sentDone(self, data):
        pass

    def sendLine(self, message):
        d = defer.Deferred()
        self.lastaction = time()
        line = ":%s\r\n" % (message)
        print "OUT>> %s" % line
        try:
            self.transport.write(line)
            d.callback(message)
        except:
            d.errback("Connection lost")
        return d

    def sendToChan(self, channels, command, message, **kw):
        if type(channels) is not list:
            channels = [channels]

        if 'prefix' not in kw.keys():
            kw['prefix'] = self.realm

        if 'notself' not in kw.keys():
            kw['notself'] = False

        for chan in channels:
            for client in chan.clients.values():
                if kw['notself'] and client == self:
                    pass
                else:
                    try:
                        client.sendMessage(command, message, to=chan.name, prefix=kw['prefix'])
                    except Exception, e:
                        print e


    def sendMessage(self, command, *params, **kw):
        if 'to' not in kw.keys():
            kw['to'] = self.nickname

        if 'prefix' not in kw.keys():
            kw['prefix'] = self.realm

        line = ' '.join([kw['prefix'], command, str(kw['to'])] + list(params))

        d = self.sendLine(line)
        d.addCallback(self.sentDone)
        d.addErrback(self.quit_cmd)

    def dataReceived(self, data):
        lines = data.split("\r\n")
        for line in lines:
            if len(line) <= 2:
                continue
            if line[-1] == "\r":
                line = line[:-1]
            print "IN << %s" % line
            c = line.split(" ")
            cmd = c[0].strip().lower()
            if len(c) > 1:
                params = c[1:]
            else:
                params = []
            self.handleCmd(cmd, params)

    def handleCmd(self, cmd, params):
        method = getattr(self, "%s_cmd" % cmd, None)
        if method:
            method(params)
        else:
            self.sendMessage(err.ERR_UNKNOWNCOMMAND, '%s :Unknown command' % cmd.upper())


    def __str__(self):
        return "<Client %s, connetcted to %s>" % (self.realm, self.server)

    __unicode__ = __str__

    __repr__ = __str__


class Server(protocol.Factory):

    protocol = Client

    def __init__(self, name):
        self.name = name
        self.clients = {}
        self.channels = {}
        self.operators = {}
        self.ophosts = ['localhost']
        print "Server %s started" % self.name

    def __str__(self):
        return "<Server %s, %i clients (%i IRCOPs) online, %i channels>" % (self.name, len(self.clients), len(self.operators), len(self.channels))

    __unicode__ = __str__

    def __repr__(self):
        return "<Server %s, %i clients (%i IRCOPs) online, %i channels>" % (self.name, len(self.clients), len(self.operators), len(self.channels))
