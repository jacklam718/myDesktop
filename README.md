myDesktop
=========

python remote desktop programe (like vnc)

Introduction
============
This program implements the server and the client, the client can control and view the server's desktop, just like using a local computer these operations, the client can use the keyboard and mouse to control the server

Libraries and APIs
==================
* The network communication used twisted and socket to achieve
* The GUI used PyQt4


##### The Keybaord and Mouse control:
* Linux    --> X11 library 
* Mac OS X --> AppKit, Quartz import
* Windows  --> win32api, ctypes


Platform
========
* Linux
* Mac OS X
* Windows
