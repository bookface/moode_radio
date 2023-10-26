#
# Gives a Window rounded corners!  Call from resizeEvent(),
#
# e.g.:
# def resizeEvent(self,event):
#     makeCornersRound(self)
#
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QImage,QBitmap

def makeCornersRound(widget):

    #
    # Would be nice if image could be create in constructor, but
    # it depends on the width and height
    #
    if not widget.isFullScreen() and not widget.isMaximized():
        image = QImage(widget.size(), QImage.Format_Mono)
        image.fill(0)

        image.setPixel(0, 0, 1)
        image.setPixel(1, 0, 1)
        image.setPixel(2, 0, 1)
        image.setPixel(3, 0, 1)
        image.setPixel(0, 1, 1)
        image.setPixel(1, 1, 1)
        image.setPixel(0, 2, 1)
        image.setPixel(0, 3, 1)

        image.setPixel(widget.width() - 4, 0, 1)
        image.setPixel(widget.width() - 3, 0, 1)
        image.setPixel(widget.width() - 2, 0, 1)
        image.setPixel(widget.width() - 1, 0, 1)
        image.setPixel(widget.width() - 2, 1, 1)
        image.setPixel(widget.width() - 1, 1, 1)
        image.setPixel(widget.width() - 1, 2, 1)
      
        image.setPixel(widget.width() - 1, 3, 1)
        
        image.setPixel(0, widget.height() - 4, 1)
        image.setPixel(0, widget.height() - 3, 1)
        image.setPixel(0, widget.height() - 2, 1)
        image.setPixel(1, widget.height() - 2, 1)
        image.setPixel(0, widget.height() - 1, 1)
        image.setPixel(1, widget.height() - 1, 1)
        image.setPixel(2, widget.height() - 1, 1)
        image.setPixel(3, widget.height() - 1, 1)
        
        image.setPixel(widget.width() - 1, widget.height() - 4, 1)
        image.setPixel(widget.width() - 1, widget.height() - 3, 1)
        image.setPixel(widget.width() - 2, widget.height() - 2, 1)
        image.setPixel(widget.width() - 1, widget.height() - 2, 1)
        image.setPixel(widget.width() - 4, widget.height() - 1, 1)
        image.setPixel(widget.width() - 3, widget.height() - 1, 1)
        image.setPixel(widget.width() - 2, widget.height() - 1, 1)
        image.setPixel(widget.width() - 1, widget.height() - 1, 1)
        widget.setMask(QBitmap.fromImage(image))



    
