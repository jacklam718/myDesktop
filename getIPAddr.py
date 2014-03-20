#!/usr/bin/env python
import socket 

def getIP( ):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('www.google.com', 80))
	addr = s.getsockname( )[0]  
	s.close( )  
	return addr
