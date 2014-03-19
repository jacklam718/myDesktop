#!/usr/bin/python
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.python import log
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import myDesktopClientProtocol as clientProtocol
import qt4reactor
import sys
import os

log.startLogging(sys.stdout)

app = QApplication(sys.argv)

__applib__  = os.path.dirname(os.path.realpath(__file__))
__appicon__ = os.path.dirname(os.path.realpath(__file__))

qt4reactor.install( )

class RDCToGUI(clientProtocol.rdc):
    def __init__(self):
        clientProtocol.rdc.__init__(self)
        self.num = 0
        self.count = 0

    def connectionMade(self):
        self.factory.readyConnection(self)

    def vncRequestPassword(self):
        password = self.factory.password
        if not password:
            password = inputbox( )
        self.sendPassword(password)

    def commitFramebufferUpdate(self, framebuffer):
        self.factory.display.updateFramebuffer(framebuffer)
        self.framebufferUpdateRequest(width=self.factory.display.width, height=self.factory.display.height)


class RDCFactory(clientProtocol.RDCFactory):
    def __init__(self, display=None, password=None, shared=0):
        clientProtocol.RDCFactory.__init__(self, password, shared)
        self.display  = display
        self.protocol = RDCToGUI

    def buildProtocol(self, addr):
        return clientProtocol.RDCFactory.buildProtocol(self, addr)

    def readyConnection(self, client):
        self.display.readyDisplay(client)
        
    def clientConnectionFailed(self, connector, reason):
        log.msg("Client connection failed!. (%s)" % reason.getErrorMessage( ))
        reactor.stop( )

    def clientConnectionLost(self, connector, reason):
        log.msg("Client connection lost!. (%s)" % reason.getErrorMessage( ))
        reactor.stop( )


class Display(QWidget):
    """
    this class for display remoteframebuffer and get the client events
    and then send the events to server, the include keyEvent, pointerEvent,
    mouseMoveEvent, clipboardEvent.
    """
    def __init__(self, parent=None):
        super(Display, self).__init__(parent)
        self.resize(1390, 780)
        self._pixelmap          = QPixmap( )
        self._remoteframebuffer = ""
        self._clipboard         = QApplication.clipboard( )
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.clientProtocol = None
        self.parent = parent

        #-------------------------------------#
        ## Use QLabel or QPainter to display ##
        #-------------------------------------#
        #self.viewPort = QLabel(self)
        #self.viewPort.setMaximumSize(self.size())
        #self.viewPort.setMinimumSize(self.size())

    def readyDisplay(self, protocol):
        self.clientProtocol = protocol
     
    def paintEvent(self, event):
        """
        paint frame buffer in widget
        """
        if self._remoteframebuffer:
            self._pixelmap.loadFromData(self._remoteframebuffer)
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._pixelmap)
            #painter.drawPixmap(0, 0, self._pixelmap.scaled(self.size( ), Qt.IgnoreAspectRatio))
        self.update( )
    
    def updateFramebuffer(self, pixelmap):
        self._remoteframebuffer = pixelmap
        #self._pixelmap.loadFromData(pixelmap)
        #self.viewPort.setPixmap(self._pixelmap)
        #self.update( )

    def keyPressEvent(self, event):
        key  = event.key( )
        print(key)
        flag = event.type( ) 
        if self.clientProtocol is None: return
        self.clientProtocol.keyEvent(key, flag)
        self.update( )

    def mousePressEvent(self, event):
        x, y   = (event.pos( ).x( ), event.pos( ).y( )) 
        button = event.button( )
        print(button)
        flag   = event.type( )
        if self.clientProtocol is None: return #self.clientProtocol = self.parent.client.clientProto
        self.clientProtocol.pointerEvent(x, y, button, flag)
        print(self.clientProtocol.pointerEvent)

    def mouseReleaseEvent(self, event):
        x, y   = (event.pos( ).x( ), event.pos( ).y( )) 
        button = event.button( )
        flag   = event.type( )
        if self.clientProtocol is None: return #self.clientProtocol = self.parent.client.clientProto
        self.clientProtocol.pointerEvent(x, y, button, flag)

    def mouseMoveEvent(self,  event):
        x, y   = (event.pos( ).x( ), event.pos( ).y( )) 
        button = event.button( )
        flag   = event.type( )
        if self.clientProtocol is None: return #self.clientProtocol = self.parent.client.clientProto
        self.clientProtocol.pointerEvent(x, y, button, flag)
        
    def resizeEvent(self, event):
        """
        the remote framebuffer's size is according the client viewer size
        this may reduce the size of the images can be
        """
        size = event.size( )
        self.width, self.height = (size.width(), size.height())


class myDesktopViewer(QMainWindow):
    def __init__(self,  parent=None):
        super(myDesktopViewer, self).__init__(parent)
        self.display = Display(self)
        self.setupUI( )

    def setupUI(self):
        self.setWindowTitle('myDesktop (viewer)')
        self.resize(800, 600)
        QApplication.setStyle(QStyleFactory.create('cleanlooks'))
        QApplication.setPalette(QApplication.style( ).standardPalette())

        # add adction on application
        self.startAction = QAction(QIcon(os.path.join(__appicon__, 'icons', 'Start.png')), 'Start', self)
        self.stopAction  = QAction(QIcon(os.path.join(__appicon__, 'icons', 'Stop.png')),  'Stop',  self)
        self.startAction.setToolTip('Start connection')
        self.stopAction.setToolTip('Stop connection')
        self.startAction.triggered.connect(self.connectionStart)
        self.stopAction.triggered.connect(self.connectionStop)

        # add a toolbar
        self.toolbar = self.addToolBar('')
        self.toolbar.addAction(self.stopAction)
        self.toolbar.addAction(self.startAction)

        displayWidget = QWidget( )
        vbox   = QVBoxLayout(displayWidget)
        vbox.addWidget(self.display)
        vbox.setMargin(0)
        self.setCentralWidget(displayWidget)

    def connectionStart(self):
        self.client = RDCFactory(display=self.display, password='1234')
        reactor.connectTCP('192.168.1.103', 5000, self.client)
        
    def connectionStop(self):
        reactor.stop( )

    def closeEvent(self, event):
        self.connectionStop( )
        exit( )

if __name__ == '__main__':
    from twisted.internet import reactor
    mydesktop = myDesktopViewer( )
    mydesktop.show( )
    reactor.run( ) # enter mainloop
