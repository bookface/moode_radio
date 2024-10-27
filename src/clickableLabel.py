from PySide6.QtCore import Qt,Signal,QTimer
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont,QFontMetrics,QMouseEvent

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# QLabels are not normally "clickable," so we need to add the signal
# March 7, 2024 - added scrolling if text doesn't fit within space
#
class ClickableLabel(QLabel):

    # signals must be declared before init in Python
    mousePress = Signal(QMouseEvent)
    
    def __init__(self,parent = None):
        super().__init__(parent)
        self.scroll_speed = 2  # Adjust the scroll speed as needed
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_text)
        # create a scrolling label within a label!
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color:rgba(0,0,0,0)")
        self.scroll = True

    #
    # scrolling is on by default, but it can be disabled
    # to save CPU cycles
    #
    def setScroll(self,boolean):
        self.scroll = boolean
        # turn off if enabled, and set "inner" label to ''
        if self.scroll == False:
            self.scrollEnabled = False
            self.scroll_timer.stop()
            self.label.setText('')
            super().setText(self.text) # restore text
        else:
            self.setText(self.text)

    # assign new text and determine if it needs to scroll.
    # If so, start the timer
    def setText(self,text):

        # scrolling turned off, just assign the text to the
        # label
        
        self.text = text
        if self.scroll == False:
            super().setText(text)
            return

        # assign to inner label
        super().setText('')           # remove text
        self.label.setText(self.text) # assign to inner label
        
        # determine if scrolling is required
        font = self.font()
        fm = QFontMetrics(font)
        r = fm.boundingRect(self.text)
        textWidth = r.width()
        self.scrollEnabled = (textWidth > self.width())

        pos = self.label.pos()
        if self.scrollEnabled == False: # center the text
            mid = self.width() / 2
            x = mid - textWidth / 2
            self.label.move(x, pos.y())
            self.scroll_timer.stop()
        else:
            self.scroll_timer.start(40)
            
    def setGeometry(self,rect):
        super().setGeometry(rect)
        self.label.setFixedSize(rect.width()*2,rect.height())
        
    # called via timer to scroll the text
    def scroll_text(self):
        if self.scrollEnabled:
            pos = self.label.pos()
            new_x = pos.x() - self.scroll_speed
            if new_x + self.width() < 0:
                new_x = self.width()  # Reset position when fully scrolled
            self.label.move(new_x, pos.y())
        
    def mousePressEvent(self,event):
        self.mousePress.emit(event)

