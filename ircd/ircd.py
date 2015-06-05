#!/usr/bin/env python
# coding: utf8

# ircd.py
# created: 2015-06-05 10:13:34
# Copyright @ 2015 breaker <breaker@broken.su>

__version__ = '0.1a'
__author__ = 'breaker <breaker@broken.su>'
__date__ = '2015-06-05'

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from lib.irc import Server

if __name__ == '__main__':
    server = TCP4ServerEndpoint(reactor, 6667)
    server.listen(Server('dumb'))
    reactor.run()
