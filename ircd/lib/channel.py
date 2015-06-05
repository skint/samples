# coding: utf8

# channel.py
# created: 2015-06-05 01:33:12
# Copyright @ 2015 breaker <breaker@broken.su>

__version__ = '0.1a'
__author__ = 'breaker <breaker@broken.su>'
__date__ = '2015-06-05'

import re


class Channel(object):

    def __init__(self, name, owner):
        # valid_channame = re.compile(r"^[&#][^\x00\x07\x0a\x0d ,:]{0,200}$")
        valid_channame = re.compile(r"^[&#][^\x07 ,:]{0,200}$")
        if valid_channame.match(name):
            self.name = name
            if name in owner.server.channels.keys():
                raise AssertionError("Channel already exists!")
        else:
            raise ValueError("Channel name not valid!")
        self.topic = ""
        self.topic_author = ""
        self.clients = {owner.nickname: owner}
        self.o = [owner]
        self.p = False
        self.s = False
        self.i = False
        self.t = False
        self.n = False
        self.m = False
        self.l = None
        self.b = []
        self.v = []
        self.k = None
        owner.channels[self.name] = self
        owner.server.channels[self.name] = self

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def __repr__(self):
        return "<Channel %s, %i clients (%i operators) online>" % (self.__str__(), len(self.clients), len(self.o))
