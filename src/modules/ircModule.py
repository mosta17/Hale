################################################################################
#   (c) 2010, The Honeynet Project
#   Author: Patrik Lantz  patrik@pjlantz.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################

import moduleManager
import threading
import socket
import re

from utils import *

@moduleManager.register("irc")
def handle_config(config, identifier):
    """
    Function to register modules, simply
    implement this to pass along the config
    and start the module thread
    """

    irc = IRC(config)
    threadManager.ThreadManager().add(irc, identifier)

class IRC(threading.Thread):

    def __init__(self, config):
        """
        Constructor sets up configs etc.
        """
       
        self.continueThread = True
        self.config = config
        self.url_expre = re.compile(self.config['url_regexp'])
        self.currentTopicInfo = ""
        threading.Thread.__init__ (self)
   
    def __doConnect(self):
        """
        Setup socket and connect to irc server, then join channel
        """

        self.irc = socks.socksocket()
        self.irc.setproxy(socks.PROXY_TYPE_SOCKS5, 'pjlantz.com', 1020)
                
        self.irc.connect((self.config['network'], int(self.config['port'])))
        self.irc.send(self.config['nick_grammar'] + ' ' + self.config['nick'] + '\r\n')
        self.irc.send(self.config['user_grammar'] + ' ' + self.config['username'] + ' ' + 
        self.config['username'] + ' ' + self.config['username'] + ' :' + self.config['realname'] + '\r\n')
        self.irc.send(self.config['join_grammar'] + ' ' + self.config['channel'] + ' ' + self.config['channel_pass'] + '\r\n')
       
    def doStop(self):
        """
        Stop this thread
        """
       
        self.continueThread = False
        self.irc.shutdown(socket.SHUT_RDWR)
       
    def run(self):
        """
        Make connection and define thread loop
        """
       
        self.__doConnect()
        while (self.continueThread):
            self.__handleIncoming()
    
    def lookForUrl(self, line):
        """
        Check for urls and download possible files
        for later analysis
        """
        
        match = self.url_expre.findall(line)
        if match:
            for entry in match:
                url = entry[0]
                print url
                   
    def __handleIncoming(self):
        """
        Handle incoming irc protocol and responses
        """
        
        data = self.irc.recv(1024)
        contents = data.split(" ")
        if data.find(self.config['ping_grammar']) != -1: # Ping
            self.irc.send(self.config['pong_grammar'] + ' ' + data.split()[1] + '\r\n') # Pong
        if data.find(self.config['topic_grammar']) != -1: # Topic
            self.lookForUrl(data)
        if data.find(self.config['currenttopic_grammar']) != -1: # Current topic
            self.lookForUrl(data)
            self.currentTopicInfo = data
            # data.split('\r\n')[0] - currenttopic, data.split('\r\n')[1] topicinfo
            # data.split('\r\n')[2...n-1] where n is the last entry shows usernames