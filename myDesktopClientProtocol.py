#!/usr/bin/python
"""
This is RDC(Remote Desktop Control) protocol
"""
from twisted.internet.protocol import Protocol, Factory, ClientFactory 
from twisted.python import log
from message_defines import messageTypes as msgTypes
import sys
import os
import time
import base64


class rdc(Protocol): 
    def __init__(self): 
        self._packet       = ""
        self._expected_len = 0
         
    def _doClientInitialization(self):
        self.framebufferUpdateRequest(width=800, height=600)
        pass

    def dataReceived(self, data):
        self._packet += data
        if self._expected_len == 0: 
            buffer = data.split('@')
            self._expected_len, self._packet = int(buffer[0]), "@".join(buffer[1:])
        
        if len(self._packet) == self._expected_len:
            cmd = eval(self._packet)
            for key in cmd.keys( ): 
                args = cmd[key]
            
            self._packet       = "" 
            self._expected_len = 0 
            self.handler(key, args)

    def _pack(self, message, **kw):
        message = "{%s: %s}" % (message, kw)
        message_len = len(message)
        message = "%s@%s" % (message_len, message)
        return message

    def handler(self, option, args): 
        #log.msg('handler')
        if option == msgTypes.AUTHENTICATION:
            print('Auth   ', args)
            self._handleAuth(**args)

        elif option == msgTypes.FRAME_UPDATE:
            self._handleFramebufferUpdate(**args)

        elif option == msgTypes.COPY_TEXT:
            self.handleCopyText(**args)

        elif option == msgTypes.CUT_TEXT:
            self._handleServerCutText(**args)

        elif option == msgTypes.TEXT_MESSAGE: 
            self.handleServerTextMessage(**args)

        elif option == msgTypes.AUTH_RESULT:
            self._handleVNCAuthResult(**args)

    #--------------------------#
    ## Handle server messages ##
    #--------------------------#
    def _handleAuth(self, block): 
        if block == 0:  # fail
            pass 

        elif block == 1:
            self._doClientInitialization( )

        elif block == 2:
            self._handleVNCAuth( )

    def _handleVNCAuth(self): 
        self.vncRequestPassword( )

    def _handleVNCAuthResult(self, block): 
        if block == 0:   # OK 
            self._doClientInitialization( )

        elif block == 1: # Failed
            self.vncAuthFailed("autenthication failed")
            #self.transport.loseConnection( )

        elif block == 2: # Too many
            self.vncAuthFailed("too many tries to log in")
            self.transport.loseConnection( )
        
        else:
            log.msg("unknown auth response (%d)\n" % auth)

    def _handleFramebufferUpdate(self, framebuffer):
        self.commitFramebufferUpdate(framebuffer)

    def vncAuthFailed(self, reason):
        log.msg('Cannot connect: %s' % reason) 

    #-----------------------------#
    ## Client >> Server messages ##
    #-----------------------------#
    def framebufferUpdateRequest(self, width, height):
        self.transport.write(self._pack(msgTypes.FRAME_UPDATE, width=width, height=height))
        
    def keyEvent(self, key, flag):
        self.transport.write(self._pack(msgTypes.KEY_EVENT, key=key, flag=flag))

    def pointerEvent(self, x, y, buttonmask, flag=None):
        self.transport.write(self._pack(msgTypes.POINTER_EVENT, x=x, y=y, buttonmask=buttonmask, flag=flag))

    def clientCutText(self, text): 
        log.msg("clientCutText; text=%s" % (text))
        self.transport.write(self._pack(msgTypes.CUT_TEXT, text=text))

    def sendPassword(self, password):
        self.transport.write(self._pack(msgTypes.AUTHENTICATION, client_password=password))

    #----------------------------#
    ## Overiding on application ##
    #----------------------------#
    def commitFramebufferUpdate(self, framebuffer):
        pass

class RDCFactory(ClientFactory):
    protocol = rdc
    def __init__(self, password=None, shared=0):
        self.password = password
        self.shared   = shared
