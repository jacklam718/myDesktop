#!/usr/bin/python
"""
this program responsible image split, merge, or the basic 
image matching
"""

from PyQt4.QtGui import (QApplication, 
                         QPixmap,
                         QImage, 
                         qRgba, 
                         qGray, 
                         qAlpha)

from PyQt4.QtCore import QSize

def grab( ):
    pix = QPixmap.grabWindow(QApplication.desktop( ).winId( ))
    return pix.toImage( )

def resize(image, width, height):
    return image.scaled(width, height)

def crop(image, x, y, width, height):
    return image.copy(x, y, width, height)

def toGray(image):
    w, h = (image.width(), image.height())
    for x in xrange(w):
        for y in xrange(h):
            pixel = image.pixel(x, y)
            gray  = qGray(pixel)
            alpha = qAlpha(pixel)
            image.setPixel(x, y, qRgba(gray, gray, gray, alpha))
    return image

def getPixel(image):
    w, h = (image.width( ), image.height( ))
    pixels = [image.pixel(x, y) for x, y in zip(xrange(w), xrange(h))]
    return pixels

def getGrayPixel(image):
    w, h = (image.width( ), image.height( ))
    pixels = [qGray(image.pixel(x, y)) for x, y in zip(xrange(w), xrange(h))] 
    return pixels

def isDiff(image1, image2, gray=False):
    """
    get the two images of pixels data or gray pixels data
    and then to  judged the image1 and image2 of pixels data 
    is same or different
    """
    if gray:
        pixels1 = getGrayPixel(image1)
        pixels2 = getGrayPixel(image2)
    else:
        pixels1 = getPixel(image1)
        pixels2 = getPixel(image2)
    return sum(pixels1) != sum(pixels2)

def calculate(image1, image2, size):
    """
    calculate two images whether are different and find out
    which parts are different in the images  
    """  
    w, h = size
    partWidth, partHeight = (w/8, h/8)
    pixelmap = [ ]
    for x in xrange(0, w, partWidth):
        for y in xrange(0, h, partHeight):
            chunk1 = crop(image1, x, y, partWidth, partHeight)
            chunk2 = crop(image2, x, y, partWidth, partHeight)
            if isDiff(image1=chunk1, image2=chunk2, gray=True):
                pixelmap.append([chunk2, x, y, partWidth, partHeight])
    return pixelmap
