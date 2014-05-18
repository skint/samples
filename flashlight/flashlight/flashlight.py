#!/usr/bin/env python
# coding: utf8

# flashlight.py
# created: 2014-05-17 13:48:40

__author__ = 'breaker <breaker@broken.su>'
__date__ = '2014-05-17'

import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.websocket
import tornado.template
import socket
import binascii
import sys
import os


class FlashlightHandlerOne(object):
    """Engine with stream.read_bytes()"""
    def __init__(self, sock=None):
        print "Starting %s" % self.__doc__
        self.actions = {
            '\x12': self.powerOn,
            '\x13': self.powerOff,
            '\x20': self.setColor,
            # '\x30': self.explode,
        }
        self.powered = False
        self.stream = tornado.iostream.IOStream(sock)
        self._read_head()

    def _read_head(self):
        self.stream.read_bytes(3, self._parse_cmd)

    def _parse_cmd(self, data):
        cmd = data[0]
        size = sum(map(ord, list(data[1:])))
        try:
            self.actions[cmd](size)
        except:
            self._read_head()

    def powerOn(self, size=None):
        print "Power ON"
        WSHandler.send_update("on")
        self.powered = True
        self._read_head()

    def powerOff(self, size=None):
        print "Power OFF"
        WSHandler.send_update("off")
        self.powered = False
        self._read_head()

    def setColor(self, size=None):
        def realSet(color):
            if self.powered:
                value = "".join(binascii.hexlify(b) for b in list(color))
                print "Change color to %s" % value
                WSHandler.send_update(value)
        self.stream.read_bytes(size, realSet)
        self._read_head()

    # def explode(self, size=None):
    #     WSHandler.send_update("explode")
    #     self._read_head()


class FlashlightHandlerTwo(object):
    """Engine with stream.read_until_close()"""
    def __init__(self, sock=None):
        print "Starting %s" % self.__doc__
        self.actions = {
            '\x12': self.powerOn,
            '\x13': self.powerOff,
            '\x20': self.setColor,
            # '\x30': self.explode,
        }
        self.powered = False
        self.stream = tornado.iostream.IOStream(sock)
        self._read_head()

    def _read_head(self):
        self.stream.read_until_close(self._closed, self._parse_cmd)

    def _closed(self, data):
        pass

    def _parse_cmd(self, packet):

        def processData(data):
            cmd = data[0]
            size = sum(map(ord, list(data[1:3])))
            if size > 0:
                payload = data[3:size + 3]
            else:
                payload = None
            try:
                self.actions[cmd](payload)
            except:
                return data[3 + size:]
            return data[3 + size:]

        idx = packet
        while len(idx) > 0:
            idx = processData(idx)

    def powerOn(self, payload=None):
        print "Power ON"
        WSHandler.send_update("on")
        self.powered = True
        self._read_head()

    def powerOff(self, payload=None):
        print "Power OFF"
        WSHandler.send_update("off")
        self.powered = False
        self._read_head()

    def setColor(self, payload=None):
        def realSet(color):
            if self.powered:
                print "Change color to %s" % color
                WSHandler.send_update(color)
        if payload and len(payload) == 3:
            color = "".join(binascii.hexlify(b) for b in list(payload))
            realSet(color)
        self._read_head()

    # def explode(self, payload=None):
    #     WSHandler.send_update("explode")
    #     self._read_head()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # root = os.path.dirname(__file__)
        # loader = tornado.template.Loader(os.path.join(root, 'tmpl'))
        # self.write(loader.load("index.html").generate())
        self.render('index.html', srvhost = self.request.host)


class WSHandler(tornado.websocket.WebSocketHandler):

    waiters = set()

    def open(self):
        print 'connection opened...'
        WSHandler.waiters.add(self)

    def on_close(self):
        WSHandler.waiters.remove(self)
        print 'connection closed...'

    @classmethod
    def send_update(cls, message):
        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                pass


class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', WSHandler),
            (r'/', MainHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": "/tmp"})
        ]
        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), 'tmpl'),
        }
        tornado.web.Application.__init__(self, handlers, **settings)


def main(address="127.0.0.1", engine=2):
    engines = {
        1: FlashlightHandlerOne,
        2: FlashlightHandlerTwo,
    }

    if engine not in engines.keys():
        print "Engine can be one of %s" % engines.keys()
        exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    try:
        s.connect((address, 9999))
    except socket.error, e:
        print "Error: %s" % e.strerror
        exit()
    engines[engine](s)
    app = App()
    app.listen(8888)
    ioloop = tornado.ioloop.IOLoop.instance()
    try:
        print "Listening on http://0.0.0.0:8888"
        ioloop.start()
    except KeyboardInterrupt:
        ioloop.stop()
        print "\nClean exit."


def run():

    if len(sys.argv) == 1:
        addr = "127.0.0.1"
        engine = 2
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        engine = 2
    elif len(sys.argv) >= 3:
        addr = sys.argv[1]
        try:
            engine = int(sys.argv[2])
        except:
            print "Engine must be integer"
            exit()

    main(addr, engine)

if __name__ == "__main__":
    run()
