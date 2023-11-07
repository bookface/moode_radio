#-*- coding: utf-8 -*-
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

from PySide6 import QtCore, QtGui, QtWidgets

from PySide6.QtCore import (Qt, QPoint, QPointF, QSize, QEvent,
                            QRect,QTimer, Signal, QSettings)

from PySide6.QtWidgets import (QApplication, QMainWindow, QFrame,
                               QMessageBox, QWidget, QLabel, QSizePolicy,
                               QVBoxLayout, QToolTip, QDial,
                               QPushButton, QMenu, QListView,QComboBox)

from PySide6.QtGui import (QPixmap,QPalette,QImage,QPainter,
                           QHoverEvent, QBrush,QPen,QFont,
                           QTransform,QCursor,QAction)

import subprocess
from subprocess import CREATE_NO_WINDOW

from roundCorners import makeCornersRound
from stationView  import StationView

import os

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
url_for_moodeview = 'http://moode.local'
image =             'images/radio1.png'
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Commands require the ip number, the browser requires the "local" name.
# Must be a Windows thing.
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# These are default settings - use moode_radio.ini to set values
url = '192.168.10.67'
# the name of each Radio Button - needs to match the image file if
# logos are enabled
buttons = ["Majestic Jukebox","FluxFM - Jazzradio Schwarzenstein",
          "FluxFM - 80s","Radio Paradise - Mellow","KRFC"]
# the url to load for each Radio Button
stations = ['http://uk3.internet-radio.com:8405/live',
            'https://fluxmusic.api.radiosphere.io/channels/jazz-schwarzenstein/stream.aac?quality=4',
            'https://fluxmusic.api.radiosphere.io/channels/80s/stream.aac?quality=4',
            'https://stream.radioparadise.com/mellow-320',
            'https://ice24.securenetsystems.net/KRFCFM?playSessionID=AA58FC61-C29C-C235-CC97982D7A692354' ]

# whatever browser to load - see symbol()
# set to True if using an alternate browser, else it will load the
# (slow) python-based browser
python_browser = False
# the alternate browser
browser_executable = "F:/apps/bin/moodeView.exe"

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# A QMainwindow with an image
# The default scale is just the size of the image file.  It can be scaled
# by applying a scale parameter
class BorderLessWindow(QMainWindow):

    def __init__(self,scale = 1.0):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pressPos = None        
        self.useRight = False
        self.resize(800,600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.imageLabel = QLabel(self)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setFrameShape(QFrame.NoFrame)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.imageLabel.scaledContents = True
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.imageLabel)
        central_widget.setLayout(self.layout)

        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.installEventFilter(self)

        self.ctrl = False
        self.alt = False

        self.scale = scale
        self.loadImage(image)
        
    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # ToolTip is returned when hovering, QHoverEvent doesn't register
    def eventFilter(self, object, event):
        # got to be a better way
        s = str(event)
        if "QEvent::ToolTip" in s:
            self.hover(event)
        return False

    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # load a single image from a file
    def loadImage(self,fileName):
        image = QImage(fileName)
        if image.isNull():
            QMessageBox.information(self,
                                    "Image Viewer",
                                    f"Cannot load {fileName}")
            return

        w = image.width()
        h = image.height()
        # call self.setAttribute(Qt.WA_TranslucentBackground) for
        # transparent background
        self.pixmap = QPixmap.fromImage(image)
        sz = QSize(w, h) # self.width(),self.height())
        if self.scale != 1.0:
            sz = QSize(w * self.scale, h*self.scale)
        self.resize(sz) # w/2,h/2)

        # aspect = Qt.IgnoreAspectRatio
        aspect = Qt.KeepAspectRatio
        self.pixmap = self.pixmap.scaled(sz,aspect,Qt.SmoothTransformation)
        self.imageLabel.setPixmap(self.pixmap)

    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def hover(self,event):      # overide this
        pass
    def rightMouse(self):       # override this
        pass
    def leftMouse(self,e):      # override this
        pass
    
    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def mousePressEvent(self,event):
        # right button to move 
        if event.button() == Qt.RightButton:
            self.pressPos = event.position()  
            self.rightMouse()
            return
        else:
            self.pressPos = None

        if event.button() == Qt.LeftButton:
            self.pressPos = None
            self.leftMouse(event)


    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def mouseMoveEvent(self,event):
        if self.pressPos != None:  
            q = QPointF(self.x(),self.y())
            r = q + (event.position() - self.pressPos)
            self.move(int(r.x()),int(r.y()))
            
    def keyReleaseEvent(self,event):
        self.ctrl = False
        self.alt = False
        
    def keyPressEvent (self,event):
        if event.key() == Qt.Key_Escape:
            self.close()

        m = event.modifiers()
        if m == Qt.ControlModifier:
            self.ctrl = True
        elif m == Qt.AltModifier:
            self.alt = True
        # print("ALT",self.alt,"CTRL",self.ctrl)
        
        
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# not showing up
class RectangleWidget(QWidget):
    def __init__(self,parent,rect):
        super().__init__(parent)
        self.rect = rect
        
    def paintEvent(self, event):
        with QPainter(self) as painter:
            print("paint",self.rect)
            painter.setPen(QPen(Qt.black,20))
            painter.setBrush(QBrush(Qt.red))
            painter.drawRect(self.rect)
            print("done paint")
            
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# An invisible QDial
class InvisaDial(QDial):

    def __init__(self,parent = None):
        super().__init__(parent)
    def paintEvent(self,event):
        pass
    
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# QLabels are not normally "clickable," so we need to add the signal
class ClickableLabel(QLabel):

    # signals must be declared before init
    mousePress = Signal()
    
    def __init__(self,parent = None):
        super().__init__(parent)

    def mousePressEvent(self,event):
        self.mousePress.emit()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# You can specify a scale to apply to the background images. The
# rectanges will get re-sized by this scale
class MyBorderLessWindow(BorderLessWindow):
    def __init__(self):

        self.loadSettings()
        super().__init__(self.imageScale)
        self.toolTip = QToolTip(self)

        # radio button rectangles
        ytop = 500
        yheight = 530-ytop
        xwidth  = 55
        self.button0Rect = QRect(320,ytop,xwidth,yheight)
        self.button1Rect = QRect(388,ytop,xwidth,yheight)
        self.button2Rect = QRect(450,ytop,xwidth,yheight)
        self.button3Rect = QRect(512,ytop,xwidth,yheight)
        self.button4Rect = QRect(574,ytop,xwidth,yheight)

        # rectangles of other places
        self.volumeRect = QRect(135,375,250-135,480-375)
        self.tuningKnobRect = QRect(700,375,810-700,480-375)
        self.symbolRect  = QRect(457,118,500-457,180-118)
        self.songRect    = QRect(114,25,846-114,73-25)
        self.tunerRect   = QRect(270,368,692-270,482-368)
        self.logoRect    = QRect(617,123,200,200)
        
        # scale the rectangles if modifying the background
        # image scale
        if self.imageScale != 1.0:
            transform = QTransform()
            transform = transform.scale(self.imageScale,self.imageScale)
            self.button0Rect = transform.mapRect(self.button0Rect)
            self.button1Rect = transform.mapRect(self.button1Rect)
            self.button2Rect = transform.mapRect(self.button2Rect)
            self.button3Rect = transform.mapRect(self.button3Rect)
            self.button4Rect = transform.mapRect(self.button4Rect)
            self.volumeRect     = transform.mapRect(self.volumeRect)
            self.tuningKnobRect = transform.mapRect(self.tuningKnobRect)
            self.symbolRect     = transform.mapRect(self.symbolRect)
            self.songRect       = transform.mapRect(self.songRect)
            self.tunerRect      = transform.mapRect(self.tunerRect)
            self.logoRect       = transform.mapRect(self.logoRect)

        # the station list is not showing
        self.stationListShowing = False
        
        # There's no way to tell if Moode is playing or not, so any
        # command line arg says it's playing, otherwise
        # start out paused
        #
        # Oct 28, 2023 moved to start-up message box
        # 
        if False:
            if len(sys.argv) > 1:
                self.status = 1     # 1 = playing
            else:
                self.status  = 0    # 0 = paused
                self.pause()
        else:
            reply = QMessageBox.question(self, "Startup", "Is Moode Currently Playing?",
                                         QMessageBox.Yes|QMessageBox.No)

            if reply == 16384:
                self.status = 1
            else:
                self.status = 0

        # just keep the current volume
        # self.vol(45)
            
        # no worko
        #self.rv = RectangleWidget(self,self.volumeRect)
        #self.rv.move(self.volumeRect.x(),self.volumeRect.y())
        
        self.volumeDial = InvisaDial(self)
        self.volumeDial.setGeometry(self.volumeRect)
        self.volumeDial.move(self.volumeRect.x(),self.volumeRect.y())
        self.volumeDial.setPageStep(1)
        self.volumeDial.valueChanged.connect(self.volDial)
        
        # Volume plus button - not sure where to put this,
        # it didn't fit in with the radio look.
        # Just use the scroll wheel on the volume knob to
        # increment/decrement by 1
        if False:
            pixmap = QPixmap('images/plus.png')
            self.plusButton = ClickableLabel(self)
            self.plusButton.setPixmap(pixmap)
            self.plusButton.move(self.volumeRect.x() + self.volumeRect.width(),self.volumeRect.y())
            self.plusButton.resize(50,50)
            self.plusButton.setScaledContents(True)
            self.plusButton.mousePress.connect(self.volumeUp)
            self.plusButton.hide()
            
        self.label = ClickableLabel(self)
        self.label.setGeometry(self.songRect)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.label.mousePress.connect(self.currentPlaying)
        makeCornersRound(self.label)
        self.label.setStyleSheet('color:white;background-color: rgba(0,0,0,0%)');

        # logos - enabled if ./radio-logos directory exists
        self.logo = None
        if os.path.isdir('radio-logos'):
            self.logo = QLabel(self)
            self.logo.setGeometry(self.logoRect)
            self.logo.setScaledContents(True)
            
        # display currently playing
        self.currentPlaying()

        # update current playing periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.currentPlaying)
        self.timer.start(10 * 1000) # seconds

    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def setLogoImage(self,fname):
        name  = f"radio-logos/{fname}"
        image = QImage(name)
        pixmap = QPixmap.fromImage(image)
        sz = QSize(image.width(),image.height())
        pixmap = pixmap.scaled(sz,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        
    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def loadSettings(self):
        fname = 'moode_radio.ini'
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            url = settings.value('url')
            for i in range(5):
                buttons[i] = settings.value(f"button{i}")
                stations[i] = settings.value(f"station{i}")
            use_browser = settings.value('python_browser')
            python_browser = False
            if use_browser == 1:
                python_browser = True
            browser_executable = settings.value('browser_executable')
            self.imageScale = float(settings.value('scale',1.0))
            # nah, keep default volume for now
            # volume = settings.value('volume')
            # self.vol(volume)
            
        
    #  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # run an mpc command
    def cmd(self,which):
        # print("Command:",which)
        proc = f"mpc -h {url} {which}"
        subprocess.run(proc,creationflags=CREATE_NO_WINDOW)
        
    # add an action to a popup menu
    def addAction(self,name,popup,callback):
        a = QAction(name, self)
        popup.addAction(a)
        a.triggered.connect(callback)

    # popup menu
    def popupMenu(self,point):
        popup = QMenu(self)
        popup.setStyleSheet('background-color: white; selection-color:red; font-size: 20px ')
        self.addAction('Minimize',popup,self.showMinimized)
        self.addAction('Browser',popup,self.launchBrowser)
        self.addAction('Exit',popup,self.close)
        popup.exec(point)
        
    # display the currently playing song
    def currentPlaying(self):
        proc = f"mpc -h {url} current"
        result = subprocess.run(proc,creationflags=CREATE_NO_WINDOW,capture_output=True)
        # print(result.stdout)
        out = str(result.stdout)
        out = out[2:]           # remove b", whatever that is
        out = out[:-3]          # remove \n
        self.label.setText(out)
        
    # called when volume dial changed
    def volDial(self,value):
        self.vol(value)
        # str = f"Volume {value}"
        # self.toolTip.showText(event.globalPos(),str,msecShowTime = 3000)
        self.label.setText(f"Volume {value}")
        
    # one of the 5 radio buttons was pressed
    def radioButton(self,i):
        self.cmd("clear")
        self.cmd(f'add {stations[i]}')
        self.cmd("play")
        self.status = 1
        self.setLogoImage(buttons[i])
        
    def pause(self):
        self.cmd('pause')

    def play(self):
        self.cmd('play')
            
    def volumeUp(self):
        self.cmd (f'vol +1')

    def volumeDown(self):
        self.cmd(f'vol -1')
            
    def vol(self,value):
        self.cmd(f'vol {value}')

    # the tuning knob toggles play/pause
    def tuningKnob(self):
        if self.status == 0: self.play()
        else: self.pause()
        self.status = 1 - self.status
            
    # a station was selected form the station list
    def stationSelected(self):
        station_url = self.stationView.url
        if station_url != None:
            self.cmd("clear")
            self.cmd(f"add {station_url}")
            self.cmd("play")

        # display the station logo, if enabled
        name = self.stationView.name
        if name != None and self.logo != None:
            name = f"{name}.jpg"
            self.setLogoImage(name)

        self.stationView.close()
        self.stationListShowing = False
        
    def stationClosed(self):
        self.stationListShowing = False
        
    # display the station list
    def tuner(self,point):
        if self.stationListShowing == False:
            self.stationListShowing = True
            self.stationView = StationView(self)
            self.stationView.show()
            self.stationView.selected.connect(self.stationSelected)
            self.stationView.closed.connect(self.stationClosed)
            
    # start a browser by clicking on the "Phillips" image
    def symbol(self):
        point = QCursor.pos()
        point.setY(point.y()- 25)
        self.popupMenu(point)
        # self.launchBrowser()

    def launchBrowser(self):
        proc = browser_executable
        if python_browser:
            if os.name == 'nt':
                proc = f"pythonw ./browser.py {url_for_moodeview}"
            else:
                proc = f"./browser.py {url_for_moodeview}"
        subprocess.Popen(proc)
        
    # display tooltips
    def hover(self,event):
        # event.pos() is QPoint, not QPointF!
        if self.volumeRect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),"Set Volume",msecShowTime = 3000)

        elif self.button0Rect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),buttons[0],msecShowTime = 2000)
        elif self.button1Rect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),buttons[1],msecShowTime = 2000)
        elif self.button2Rect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),buttons[2],msecShowTime = 2000)
        elif self.button3Rect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),buttons[3],msecShowTime = 2000)
        elif self.button4Rect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),buttons[4],msecShowTime = 2000)

        elif self.tuningKnobRect.contains(event.pos()):
            if self.status == 0: s = 'Play'
            else: s = 'Pause'
            self.toolTip.showText(event.globalPos(),s,msecShowTime = 2000)
        elif self.tunerRect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),'Select Station',msecShowTime = 2000)
                
    # left mouse pressed
    def leftMouse(self,e):
        # position is QPointf here! Must convert to QPoint to compare to rect
        pos = e.position()
        x = pos.x(); y = pos.y()
        point = QPoint(x,y)
            
        if self.button0Rect.contains(point):
            self.radioButton(0)
        elif self.button1Rect.contains(point):
            self.radioButton(1)
        elif self.button2Rect.contains(point):
            self.radioButton(2)
        elif self.button3Rect.contains(point):
            self.radioButton(3)
        elif self.button4Rect.contains(point):
            self.radioButton(4)

        elif self.tuningKnobRect.contains(point):
            self.tuningKnob()

        elif self.symbolRect.contains(point):
            self.symbol()
        elif self.tunerRect.contains(point):
            self.tuner(point)
        else:
            print("My Left Mouse",point)

#  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    import os
                    
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = MyBorderLessWindow()
    win.show()
    sys.exit(app.exec())
