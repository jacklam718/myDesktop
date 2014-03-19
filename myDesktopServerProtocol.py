#!/usr/bin/python
from twisted.internet.protocol import Protocol, Factory
from twisted.python import log
from message_defines import messageTypes as msgTypes
import sys
log.startLogging(sys.stdout)

class RDCServerProtocol(Protocol):
    def __init__(self):
        self._packet       = ""
        self._expected_len = 0
        self.state   = "UNREGISTERED"

    def dataReceived(self, data):
        try:
            print(len(data), data)
            buffer = data.split('@')
            self._expected_len, data = int(buffer[0]), '@'.join(buffer[1:])
            cmd = eval(data[:self._expected_len])
            for key in cmd.keys( ):
                args = cmd[key]
            self._expected_len = 0
            self.handler(option=key, args=args)
        except:
            self.doFramebufferUpdate(dict(width=800, height=800))
            print('\33[31mError!\33[0m')
            
    def handler(self, option, args):
        #log.msg('handler')
        if option == msgTypes.AUTHENTICATION:
            self._handleClientAuth(**args)

        elif option == msgTypes.INITIALIZATION: 
            self.serverInitialization( )

        elif option == msgTypes.FRAME_UPDATE:
            self.doFramebufferUpdate(**args)

        elif option == msgTypes.KEY_EVENT:
            self.doKeyEvent(**args)

        elif option == msgTypes.POINTER_EVENT:
            self.doPointerEvent(**args)

        elif option == msgTypes.COPY_TEXT:
            self.doCopyText( )

        elif option == msgTypes.CUT_TEXT:
            self.doClientCutText( )

    def serverInitialization(self):
        pass

    def connectionMade(self):
        log.msg('connectionMade')
        if not self.factory.password:
            self.state = 'REGISTERED'
            self.transport.write(self._pack(msgTypes.AUTHENTICATION, block=1))
        else: 
            self.transport.write(self._pack(msgTypes.AUTHENTICATION, block=2))
        #self.readyConnection(self)

    def _handleClientAuth(self, client_password):
        log.msg('_handleClientAuth')
        if self.factory.password == str(client_password):
            self.state = 'REGISTERED'
            self.transport.write(self._pack(msgTypes.AUTH_RESULT, block=0))

        elif self.factory.password != str(client_password):
            self.transport.write(self._pack(msgTypes.AUTH_RESULT, block=1))

        elif self._logTimes >= self.logMaxTimes: 
            self.transport.write(self._pack(msgTypes.AUTH_RESULT, block=2))

    def _pack(self, key, **kw):
        message = "{%s: %s}" % (key, kw)
        message_len = len(message)
        message = "%s@%s" % (message_len, message)
        return message

    def doFramebufferUpdate(self, width=1366, height=760): 
        framebuffer = self._makeFramebuffer(width, height)
        self.transport.write(self._pack(msgTypes.FRAME_UPDATE, framebuffer=framebuffer))

    def doKeyEvent(self, key, flag=1):
        self.handleKeyEvent(key, flag)

    def doPointerEvent(self, x, y, buttonmask, flag): 
        self.handleMouseEvent(x, y, buttonmask, flag)

    def doCopyTextFromClient(self, text):
        """
        copy text from text
        """ 
        self.handleClientCopyText(text)

    #----------------------------#
    ## Server >> Client message ##
    #----------------------------#
    def sendCutTextToClient(self, text):
        """
        get server cut text to client
        """
        self.transport(self._pack(msgTypes.CUT_TEXT, text=text))
        
        
class RDCFactory(Factory):
    protocol = RDCServerProtocol
    def __init__(self, password=None): 
        self.password = password
