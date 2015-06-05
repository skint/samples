# coding: utf8

# commands.py
# created: 2015-06-04 20:32:31
# Copyright @ 2015 breaker <breaker@broken.su>

__version__ = '0.1a'
__author__ = 'breaker <breaker@broken.su>'
__date__ = '2015-06-04'

import errors as err
import replys as rpl
from channel import Channel

class commandMixin(object):

    def nick_cmd(self, params):
        if len(params) < 1:
            self.sendMessage(err.ERR_NONICKNAMEGIVEN, '%s :No nickname given' % params[0])
        try:
            self.nickname = params[0]
        except ValueError, e:
            self.sendMessage(err.ERR_ERRONEUSNICKNAME, '%s :%s' % (params[0], e))
        except AssertionError, e:
            self.sendMessage(err.ERR_NICKNAMEINUSE, '%s :%s' % (params[0], e))

    def user_cmd(self, params):
        if len(params) < 4:
            self.sendMessage(err.ERR_NEEDMOREPARAMS, "CMD :Not enough parameters")
        try:
            if not self.registered:
                self.registered = True
                self.nickname = params[0]
            else:
                self.sendMessage(err.ERR_ALREADYREGISTRED, ":You may not reregister")
        except ValueError, e:
            self.sendMessage(err.ERR_ERRONEUSNICKNAME, '%s :%e' % (params[0], e))
        except AssertionError, e:
            self.sendMessage(err.ERR_NICKNAMEINUSE, '%s :%s' % (params[0], e))


        self.hostname = params[1]
        self.servername = params[2]

        if params[3:][0].startswith(":"):
            self.realname = params[3:][1:]

        self.sendMessage(rpl.RPL_MOTDSTART, ':- Message Of The Day - ')
        self.sendMessage(rpl.RPL_MOTD, ':- MOTD DATA')
        self.sendMessage(rpl.RPL_ENDOFMOTD, ':End of /MOTD command.')

    def pass_cmd(self, params):
        self.password = params[0].split()[-1]

    def mode_cmd(self, params):
        result = None
        who = params[0]
        if who[0] in ['#', '&']:
            try:
                channel = self.server.channels[who]
                if params[1][1] in ['p', 's', 'i', 't', 'n', 'm']:
                    if params[1][0] == '+':
                        result = True
                    elif params[1][0] == '-':
                        result = False
                    self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s' % (who, params[1]))
                    setattr(channel, params[1][1], result)

                elif params[1][1] in ['l', 'k']:
                    if params[1][0] == '+':
                        value = params[2]
                    elif params[1][0] == '-':
                        value = None
                    setattr(channel, params[1][1], value)
                    self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s %s' % (who, params[1], ' '.join(params[2:])))

                elif params[1][1] == 'b':
                    if params[1][0] == '+':
                        if len(params) < 3:
                            print channel.b
                            for ban in channel.b:
                                self.sendMessage(rpl.RPL_BANLIST, "%s %s" % (who, ban))
                            self.sendMessage(rpl.RPL_ENDOFBANLIST, "%s :End of channel ban list" % who)
                            print "HERE"
                        else:
                            channel.b.append(params[2])
                            self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s %s' % (who, params[1], params[2]))
                    elif params[1][0] == '-':
                        try:
                            channel.b.remove(params[2])
                            self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s %s' % (who, params[1], params[2]))
                        except:
                            pass

                elif params[1][1] == 'o':
                    if params[1][0] == '+':
                        if len(params) < 3:
                            self.sendMessage(err.ERR_NEEDMOREPARAMS, "MODE:Not enough parameters")
                        else:
                            channel.o.append(params[2])
                    elif params[1][0] == '-':
                        try:
                            channel.b.remove(params[2])
                        except:
                            pass
                    self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s %s' % (who, params[1], params[2]))

                elif params[1][1] == 'v':
                    if params[1][0] == '+':
                        if len(params) < 3:
                            self.sendMessage(err.ERR_NEEDMOREPARAMS, "MODE :Not enough parameters")
                        else:
                            channel.v.append(params[2])
                    elif params[1][0] == '-':
                        try:
                            channel.b.remove(params[2])
                        except:
                            pass
                    self.sendMessage(rpl.RPL_CHANNELMODEIS, '%s :%s %s' % (who, params[1], params[2]))

            except Exception, e:
                print e
                self.sendMessage(err.ERR_NOSUCHCHANNEL, "%s :No such channel." % who)

        if who == self.nickname:
            if params[1][0] == '+':
                result = True
            elif params[1][0] == '-':
                result = False
            else:
                self.sendMessage(err.ERR_UMODEUNKNOWNFLAG, ':Unknown MODE flag.')

            attr = getattr(self, params[1][1], None)

            if attr is not None:
                setattr(self, params[1][1], result)
                self.sendMessage(rpl.RPL_UMODEIS, ":%s" % params[1])
            else:
                self.sendMessage(err.ERR_UMODEUNKNOWNFLAG, ':Unknown MODE flag.')

    def oper_cmd(self, params):
        if len(params) < 2:
            self.sendMessage(err.ERR_NEEDMOREPARAMS, "OPER :Not enough parameters")
        else:
            if self.hostname in self.server.ophosts:
                if params[0] == params[1]:
                    self.o = True
                    self.server.operators.append(self)
                    self.sendMessage(rpl.RPL_YOUREOPER, ":You now an IRC operator.")
                else:
                    self.sendMessage(err.ERR_PASSWDMISMATCH, ":Password incorrect.")
            else:
                self.sendMessage(err.ERR_NOOPERHOST, ":No O-lines for your host.")

    def quit_cmd(self, params):
        # XXX: send quit message to every channels
        self.sendMessage("QUIT", "%s" % ' '.join(params))
        self.transport.loseConnection()

    def join_cmd(self, params):
        if len(params) < 1:
            self.sendMessage(err.ERR_NEEDMOREPARAMS, "JOIN :Not enough parameters")
        else:
            join_channels = params[0].split(",")
            if len(params) > 1:
                join_keys = params[1].split(",")
            else:
                join_keys = []
            chans = dict(map(None, join_channels, join_keys))
            for chan in chans.keys():
                if chan not in self.server.channels.keys():
                    try:
                        c = Channel(chan, self)
                        self.sendMessage(rpl.RPL_TOPIC, "%s %s" % (chan, c.topic))
                    except Exception, e:
                        self.sendMessage(err.ERR_NOSUCHCHANNEL, '%s :%s' % (params[0], e))
                else:
                    c = self.server.channels[chan]
                    if c.k == chans[chan]:
                        c.clients[self.nickname] = self
                        self.channels[chan] = c
                        self.sendMessage(rpl.RPL_TOPIC, "%s %s" % (chan, c.topic))
                    else:
                        self.sendMessage(err.ERR_BADCHANNELKEY, ":%s" % chan)

    def topic_cmd(self, params):
        if len(params) < 1:
            self.sendMessage(err.ERR_NEEDMOREPARAMS, "TOPIC :Not enough parameters")
        else:
            try:
                chan = self.channels[params[0]]
                if len(params) > 1:
                    if self.nickname not in chan.clients.keys():
                        self.sendMessage(err.ERR_NOTONCHANNEL, "%s :You're not on that channel" % params[0])
                    elif chan.t is True and self.nickname not in chan.o:
                        # self.sendMessage(err.ERR_CHANOPRIVSNEEDED, "%s :You're not channel operator" % params[0])
                        self.sendMessage(rpl.RPL_NOTOPIC, "%s :No topic is set" % chan)
                    else:
                        chan.topic = ' '.join(params[1:])
                        chan.topic_author = self.nickname
                        for i in chan.clients.keys():
                            chan.clients[i].sendMessage(rpl.RPL_TOPIC, "%s %s" % (params[0], chan.topic))
            except Exception, e:
                print e
                self.sendMessage(err.ERR_NOSUCHCHANNEL, "%s :No such channel." % params[0])

