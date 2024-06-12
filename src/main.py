#-*- coding: utf-8 -*-
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
# donn, Mar 7, 2024
#   - added radio6 image
# donn, Mar 1, 2024
#   - move borderLessWindow to a separate file
# donn, Jan 26, 2024
#   - sorted the station view
# donn, Jan 16, 2024
#   - keep the station list open for selecting stations, previously
#     it was closed when a station was selected
# donn, Jan 15, 2024
#   - left mouse now drags if no knob is under the mouse
#   - added overlays to see positions of knobs for debugging. Might
#     change radio image if I can find another good one
# donn, Jan 14, 2024 - added timeouts to mpc
#
# volumeRect     = Volume knob
# tuningKnobRect = Tuning knob
# symbolRect     = pop-up menu place
# songRect       = text displaying currently playing
# tunerRect      = station selector
# logoRect       = station image if radio-logos exist
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

from PySide6.QtCore import (Qt, QPoint, QPointF, QSize, QEvent,
                            QRect, QTimer, Signal, QSettings)
from PySide6.QtWidgets import (QApplication, QMessageBox, QLabel,
                               QToolTip, QDial, QRubberBand,
                               QMenu,QListView)
from PySide6.QtGui import (QPixmap,QImage,QHoverEvent, QBrush,
                           QPen,QFont,QTransform,QCursor,QAction,
                           QIcon)

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
from roundCorners import makeCornersRound
from stationView  import StationView
from borderLessWindow import BorderLessWindow,RubberBandWidget
from clickableLabel import ClickableLabel

import os

# Looks like subprocess is not very portable
import subprocess
if os.name == 'nt':
    from subprocess import CREATE_NO_WINDOW

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# These are default settings - use moode_radio.ini to set values
# Commands require the ip number, the browser requires the "local" name.
# Must be a Windows thing.
#
url_for_moodeview = 'http://moode.local'
url   = '192.168.1.2'

#
# the name of each Radio Button - they need to match the name of the
# image file if logos are enabled
#
buttons = ["Majestic Jukebox",
           "FluxFM - Jazzradio Schwarzenstein",
           "FluxFM - 80s",
           "Radio Paradise - Mellow",
           "KRFC"]
#
# the url to load for each Radio Button
#
stations = ['http://uk3.internet-radio.com:8405/live',
            'https://fluxmusic.api.radiosphere.io/channels/jazz-schwarzenstein/stream.aac?quality=4',
            'https://fluxmusic.api.radiosphere.io/channels/80s/stream.aac?quality=4',
            'https://stream.radioparadise.com/mellow-320',
            'https://ice24.securenetsystems.net/KRFCFM?playSessionID=AA58FC61-C29C-C235-CC97982D7A692354' ]

#
# Whatever browser to load - see symbol().
# Set to False if using an alternate browser, else it will load the
# (slow, but works fine) python-based browser
#
python_browser = True

# the alternate browser, a separate executable
if os.name == 'nt':
    browser_executable = "C:/apps/bin/moodeView.exe"
else:
    browser_executable = "~/apps/bin/moodeView"

#
# Path to radiologos - either local downloaded via backup from moode
# or a mounted dir from /var/local/www.imagesw/radio-logos
# on the moode player.
#
# Default is local, make changes in moode_radio.ini.

radiologos = 'radio-logos'

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# An invisible QDial - rotatable, but probably easier to just use
# the mouse scroll wheel
class InvisaDial(QDial):

    def __init__(self,parent = None):
        super().__init__(parent)
    def paintEvent(self,event):
        pass
    
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# run with "-2,-3,...etc"" to load the other radio images
def parseArgs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-1',action='store_true', required = False)
    parser.add_argument('-2',action='store_true', required = False)
    parser.add_argument('-3',action='store_true', required = False)
    parser.add_argument('-4',action='store_true', required = False)
    parser.add_argument('-5',action='store_true', required = False)
    parser.add_argument('-6',action='store_true', required = False)
    args = parser.parse_args()
    dict = vars(args)           # convert to dictionary
    return dict

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Main Window
# You can specify a scale to apply to the background image. The
# rectangles will get re-sized by this scale
class MyBorderLessWindow(BorderLessWindow):
    def __init__(self):

        args = parseArgs()

        # load image and image scale
        self.group,x,y = self.getLast() # get the last saved radio
        if args["1"]:   self.group = 'Radio1'
        elif args["2"]: self.group = 'Radio2'
        elif args["3"]: self.group = 'Radio3'
        elif args["4"]: self.group = 'Radio4'
        elif args["5"]: self.group = 'Radio5'
        elif args["6"]: self.group = 'Radio6'

        # read ini file for image and scale
        self.setImageAndScale(self.group)

        super().__init__(self.image,self.imageScale)
        if x != None:
            self.move(int(x),int(y))

        # load all other settings
        self.loadSettings(self.group)
        self.toolTip = QToolTip(self)

        # set application icon,yet another Windows kludge
        if os.name == 'nt':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('moode_radio.app.1')
        pixmap = QPixmap('images/radioIcon.png')
        self.icon = QIcon(pixmap)
        self.setWindowIcon(self.icon)

        # set up the rectangles for the knobs
        self.initRectangles()          # initialize the array
        self.setRectangles(self.group) # load the array from ini file
            
        # the station list is not showing
        self.stationListShowing = False
        
        # create the volume dial
        self.volumeDial = InvisaDial(self)
        self.volumeDial.setGeometry(self.volumeRect)
        self.volumeDial.move(self.volumeRect.x(),self.volumeRect.y())
        self.volumeDial.setPageStep(1)
        self.volumeDial.valueChanged.connect(self.volDial)
        
        # label to display text at top of radio, e.g. what's
        # playing. Clicking it will update the value.
        self.label = ClickableLabel(self)
        self.label.setGeometry(self.songRect)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.label.mousePress.connect(self.currentPlaying)
        makeCornersRound(self.label)
        if self.label_style != None:
            self.label.setStyleSheet(self.label_style)
        else:
            self.label.setStyleSheet('color:white;background-color: rgba(0,0,0,0%)');

        # logos - enabled if ./radio-logos directory exists, create a label to
        # hold the image
        self.logo = None
        global radiologos
        if os.path.isdir(radiologos):
            self.logo = QLabel(self)
            self.logo.setGeometry(self.logoRect)
            self.logo.setScaledContents(True)
            self.setLogoImage('')
            
        # display currently playing
        self.currentPlaying()

        # update current playing periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.currentPlaying)
        self.timer.start(10 * 1000) # seconds

        self.status()

        # preserve the current selected row in stationView()
        self.currentRow = 0

        # continue where left off
        self.loadLastPlsFile()
        
    def getLast(self):
        group = 'Radio1'
        fname = 'moode_last.ini'
        x = 500; y = 500
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            x = settings.value("geometryX")
            y = settings.value("geometryY")
            group = settings.value("last_group")
        return group,x,y
    
    def loadLastPlsFile(self):
        fname = 'moode_last.ini'
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            plsname= settings.value("plsfile")
            if plsname != None:
                self.loadPlsFile(plsname)
        
    def closeEvent(self,event):
        fname = 'moode_last.ini'
        settings = QSettings(fname,QSettings.IniFormat)
        settings.setValue("geometryX", self.geometry().x())
        settings.setValue("geometryY", self.geometry().y())
        settings.setValue("last_group", self.group)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # create the knob rectangles and initialize with some default values
    def initRectangles(self):
        ytop = 503
        yheight = 530-ytop
        xwidth  = 55
        self.buttonRects = []

        self.buttonRects.append(QRect(320,ytop,xwidth,yheight))
        self.buttonRects.append(QRect(388,ytop,xwidth,yheight))
        self.buttonRects.append(QRect(450,ytop,xwidth,yheight))
        self.buttonRects.append(QRect(512,ytop,xwidth,yheight))
        self.buttonRects.append(QRect(574,ytop,xwidth,yheight))

        # 10 buttons max
        # for i in range(5):
        # self.buttonRects.append(QRect(0,0,0,0))

        # rectangles of other knob places
        self.volumeRect     = QRect(145,380,250-135,480-375)
        self.tuningKnobRect = QRect(703,380,810-700,480-375)
        self.symbolRect  = QRect(457,118,500-457,180-118)
        self.songRect    = QRect(114,35,846-114,73-25)
        self.tunerRect   = QRect(270,368,692-270,482-368)
        self.logoRect    = QRect(617,123,200,200)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # set the values of the rectangles. Load from ini, scale, and
    # create rubberband overlays
    def setRectangles(self,group):

        # load the rectangles from the ini file
        self.loadRectanglesFromIni(group)
        
        # scale the rectangles if modifying the background's
        # image scale
        if self.imageScale != 1.0:
            transform = QTransform()
            transform = transform.scale(self.imageScale,self.imageScale)
            for i in range(len(self.buttonRects)):
                self.buttonRects[i] = transform.mapRect(self.buttonRects[i])
            self.volumeRect     = transform.mapRect(self.volumeRect)
            self.tuningKnobRect = transform.mapRect(self.tuningKnobRect)
            self.symbolRect     = transform.mapRect(self.symbolRect)
            self.songRect       = transform.mapRect(self.songRect)
            self.tunerRect      = transform.mapRect(self.tunerRect)
            self.logoRect       = transform.mapRect(self.logoRect)

        # for debugging locations of knobs, call the popup 'toggle'
        # to turn on/off
        rubberBandWidget = self.centralWidget()
        rubberBandWidget.delete()
        for button in self.buttonRects:
            rubberBandWidget.addRectangle(button)
        rubberBandWidget.addRectangle(self.volumeRect)
        rubberBandWidget.addRectangle(self.tuningKnobRect)
        rubberBandWidget.addRectangle(self.symbolRect)
        rubberBandWidget.addRectangle(self.songRect)
        rubberBandWidget.addRectangle(self.tunerRect)
        rubberBandWidget.addRectangle(self.logoRect)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def setLogoImage(self,fname):
        global radiologos
        name  = f"{radiologos}/{fname}"
        if not os.path.isfile(name):
            name  = f"{radiologos}/{fname}.jpg"
        if os.path.isfile(name):
            self.setLogo(name)
        else:
            name  = 'images/notfound.png'
            self.setLogo(name)

    def setLogo(self,name):
        image = QImage(name)
        pixmap = QPixmap.fromImage(image)
        sz = QSize(image.width(),image.height())
        pixmap = pixmap.scaled(sz,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        if self.logo != None:
            self.logo.setPixmap(pixmap)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # cmdResult() sometimes comes out as:
    #  :b'volume: 21%   repeat: off   random: off   single: off   consume: off'
    # other times it's an array, so have to figure out via the length
    # returned what we are getting back
    #
    # sets the value of the volume dial
    def status(self):
        result = self.cmdResult('')
        if len(result) == 0:
            return
        out = str(result[len(result)-1])
        if 'ERROR' in out:
            self.label.setText(out)
            return
        out = out[2:]           # remove b", whatever that is
        tokens = out.split()
        out = tokens[1]         # should be volume number
        out = out[:-1]          # remove the %
        self.volumeDial.setValue(int(out))

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # set the name of the image and it's scale
    def setImageAndScale(self,group):
        # defaults
        self.image = 'images/radio1.png'
        self.imageScale = 1.0
        self.label_style = None
        fname = 'moode_system.ini'
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            if group != None:
                settings.beginGroup(group)
            r = settings.value("image")
            if r != None:
                self.image = r
            r = settings.value("scale")
            if r != None:
                self.imageScale = float(r)
            r = settings.value("label_style")
            if r != None:
                self.label_style = r
                

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # load settings from ini files.  moode_system.ini contains settings for
    # all radios, and would generally be modified only if adding a radio
    # image. moode_radio.ini is for settings local to this
    #
    def loadSettings(self,group):
        # get num buttons from system file
        fname = 'moode_system.ini'
        numButtons = 5
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            if group != None:
                settings.beginGroup(group)
            numButtons = int(settings.value('numButtons',5))

        # load personal settings next
        fname = 'moode_radio.ini'
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            global url,stations,buttons
            url = settings.value('url')
            for i in range(5):  # 5 buttons default
                v = settings.value(f"button{i}")
                if v != None:
                    buttons[i] = v
                v = settings.value(f"station{i}")
                if v != None:
                    stations[i] = v

            #
            # use the built-in python browser or use an
            # alternative
            #
            global use_python_browser,python_browser
            global browser_executable
            s = settings.value('python_browser')
            if s != None:
                use_python_browser = s
                python_browser = (int(use_python_browser) == 1)
            s = settings.value('browser_executable')
            if s != None:
                browser_executable = settings.value('browser_executable')

            # radio logos - local directory or smb mounted
            global radiologos
            s = settings.value('radiologos')
            if s != None:
                radiologos = s
                
        # default is 5 buttons. Some radios can contain more then
        # 5, so load any additional buttons 
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            settings.beginGroup(group)
            for i in range(numButtons):
                v = settings.value(f"button{i}")
                if v != None:
                    buttons.append(v)
                v = settings.value(f"station{i}")
                if v != None:
                    stations.append(v)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # load the rectanges defining the clickable buttons
    def loadRectanglesFromIni(self,group):
        fname = 'moode_system.ini'
        if os.path.isfile(fname):
            settings = QSettings(fname,QSettings.IniFormat)
            if group != None:
                settings.beginGroup(group)
            numButtons = int(settings.value('numButtons',5))
            for i in range(numButtons):
                r = settings.value(f"buttonRect{i}")
                if r != None:
                    if i < len(self.buttonRects):
                        self.buttonRects[i] =QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
                    else:
                        self.buttonRects.append(QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3])))

            r = settings.value('volumeRect')
            if r != None: self.volumeRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
            r = settings.value('tuningKnobRect')
            if r != None: self.tuningKnobRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
            r = settings.value('symbolRect')
            if r!= None: self.symbolRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
            r = settings.value('songRect')
            if r!= None:self.songRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
            r = settings.value('tunerRect')
            if r!= None: self.tunerRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))
            r = settings.value('logoRect')
            if r!= None: self.logoRect = QRect(int(r[0]),int(r[1]),int(r[2]),int(r[3]))

            r = settings.value('station5')
            if r != None:
                buttons.append(settings.value('button5'))
                stations.append(settings.value("station5"))

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # run an mpc command
    def cmd(self,which):
        proc = f"mpc --quiet -h {url} {which}"
        try:
            if os.name == 'nt':
                subprocess.run(proc,creationflags=CREATE_NO_WINDOW,timeout = 3,check=True)
            else:
                subprocess.run(proc,shell=True,timeout = 3,check=True)
        except:
            self.label.setText(f"MPC Error, check URL:{url}")
        
    #
    # run an mpc command, and return the result strings.
    # Sometimes we only get a single string back, sometimes an
    # array of strings!
    #
    def cmdResult(self,which):
        import signal
        result = []
        proc = f"mpc -h {url} {which}"
        try:
            process = subprocess.Popen(proc,shell=True,
                                       stdin=None,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            process.wait(timeout=1)
            result=process.stdout.readlines()
        except subprocess.TimeoutExpired:
            self.label.setText(f"Error In Communication, check URL:{url}")
            os.kill(process.pid, signal.SIGTERM)

        return result

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # return the length of the playlist
    def playlistLength(self):
        result = self.cmdResult('playlist')
        return len(result)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # add a url to the bottom of the playlist and play it
    def add(self,url):
        self.setLogoImage('')
        self.cmd(f'add {url}')
        result = self.playlistLength()
        if result > 0:
            self.cmd(f"play {result}")
            return True
        return False
    
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # load a 'pls' playlist file
    def load(self,name):
        self.setLogoImage('')
        self.cmd(f"load '{name}'")
        result = self.playlistLength()
        if result > 0:
            self.cmd(f"play {result}")
            return True
        return False
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # clears the playlist
    def clearList(self):
        self.cmd('clear');
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # just for debugging, show the locations of knobs, etc.
    def toggleOverlays(self):
        rubberBandWidget = self.centralWidget()
        rubberBandWidget.toggle()
            
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # add an action to a popup menu
    def addAction(self,name,popup,callback):
        a = QAction(name, self)
        popup.addAction(a)
        a.triggered.connect(callback)

    # easiest way to change the radio image is to just
    # restart the program
    def restart(self,arg):
        if os.name == 'nt':
            os.execv(sys.executable, [f"pythonw main.py {arg}"])
        else:                   # linux
            os.execl(sys.executable, 'python3', __file__, arg)
        
    def radio1(self):
        self.restart('-1')

    def radio2(self):
        self.restart('-2')

    def radio3(self):
        self.restart('-3')

    def radio4(self):
        self.restart('-4')

    def radio5(self):
        self.restart('-5')

    def radio6(self):
        self.restart('-6')
            
    def toggleLabelScroll(self):
        self.label.setScroll(not self.label.scroll)
        # self.label.setText(self.label.text)
        
    # popup menu
    def popupMenu(self,point):
        popup = QMenu(self)
        popup.setStyleSheet('background-color: white; selection-color:red; font-size: 20px ')
        self.addAction('Radio 1',popup,self.radio1)
        self.addAction('Radio 2',popup,self.radio2)
        self.addAction('Radio 3',popup,self.radio3)
        self.addAction('Radio 4',popup,self.radio4)
        self.addAction('Radio 5',popup,self.radio5)
        self.addAction('Radio 6',popup,self.radio6)
        self.addAction('Next Song',popup,self.next)
        self.addAction('Previous Song',popup,self.prev)
        self.addAction('Minimize',popup,self.showMinimized)
        self.addAction('Browser',popup,self.launchBrowser)
        self.addAction('Clear Playlist',popup,self.clearList)
        self.addAction('Crop Playlist',popup,self.crop)
        self.addAction('Toggle Scroll',popup,self.toggleLabelScroll)
        self.addAction('Toggle Overlays',popup,self.toggleOverlays)
        self.addAction('Exit',popup,self.close)
        popup.exec(point)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # display the currently playing song
    def currentPlaying(self):
        result = self.cmdResult('current')
        if len(result) == 1:
            out = str(result)
            out = out[3:]           # remove b"', whatever that is
            out = out[:-4]          # remove trailing slash and \n
            self.label.setText(out)
            #
            # Would be nice to figure out the logo from
            # what's currently playing, but mpc 'current'
            # is not going to match the logo images.
            # self.checkLogoImage(whatsPlaying)

    def next(self):
        self.cmd('next')

    def prev(self):
        self.cmd('prev')
        
    # clears playlist except for current
    def crop(self):
        self.cmd('crop')
        
    # called when volume dial changed
    def volDial(self,value):
        self.vol(value)
        # str = f"Volume {value}"
        # self.toolTip.showText(event.globalPos(),str,msecShowTime = 3000)
        self.label.setText(f"Volume {value}")
        
    # one of the radio buttons was pressed
    def radioButton(self,i):
        if self.add(stations[i]) == True:
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
        self.cmd('toggle')
            
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # We now load pls file obtained from moode instead if using the url.
    # Using the pls file also makes it easier to load the jpg, since the
    # names are identical
    def loadPlsFile(self,plsname):
        name = f"RADIO/{plsname}" # see stationView, add RADIO
        self.load(name)
        if self.logo != None:
            name = plsname.replace('.pls', "", 1)
            name = f"{name}.jpg"
            self.setLogoImage(name)
        # save it
        fname = 'moode_last.ini'
        settings = QSettings(fname,QSettings.IniFormat)
        settings.setValue("plsfile", plsname)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # a station was selected form the station list
    def stationSelected(self):
        #
        # This new version uses pls files obtained from moode,
        # not the url from the json file.
        # If station_url is None, then we load the .pls file
        #
        station_url = self.stationView.url
        if station_url == None:
            plsname = self.stationView.name
            self.loadPlsFile(plsname)
        else:
            if self.add(station_url) == True:
                name = self.stationView.name
                # display the station logo, if enabled
                if name != None and self.logo != None:
                    name = f"{name}.jpg"
                    self.setLogoImage(name)
                    #print(f"SELECTED:{station_url} NAME:{name}")
                    
    # set a flag indicating the list is not showing and preserve the
    # currently selected row
    def stationClosed(self,row):
        self.currentRow = row
        self.stationListShowing = False
        
    # display the station list
    def tuner(self,point):
        if self.stationListShowing == False:
            self.stationListShowing = True
            self.stationView = StationView(self.currentRow,url,self)
            self.stationView.show()
            self.stationView.selected.connect(self.stationSelected)
            self.stationView.closed.connect(self.stationClosed)
            
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # start a browser
    def symbol(self):
        point = QCursor.pos()
        point.setY(point.y()- 25)
        self.popupMenu(point)

    def launchBrowser(self):
        global url_for_moodeview,python_browser
        proc = browser_executable
        cwd = os.getcwd()

        # subprocess requires shell=True on linux for some
        # stupid reason. Otherwise it can't find the python
        # executable.

        if python_browser:      # use python browser
            if os.name == 'nt':
                proc = f"pythonw ./browser.py {url_for_moodeview}"
                subprocess.Popen(proc)
            else:
                proc = f"python3 browser.py {url_for_moodeview}"
                subprocess.Popen(proc,shell=True,cwd=cwd)
        else:                   # use alternative browser
            subprocess.Popen(browser_executable)
            
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # display tooltips
    def hover(self,event):
        # event.pos() is QPoint, not QPointF!
        if self.volumeRect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),"Set Volume",msecShowTime = 3000)
        elif self.tuningKnobRect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),'Play/Pause',msecShowTime = 2000)
        elif self.tunerRect.contains(event.pos()):
            self.toolTip.showText(event.globalPos(),'Select Station',msecShowTime = 2000)
        else:
            for i in range(len(self.buttonRects)):
                if self.buttonRects[i].contains(event.pos()):
                    if i < len(buttons):
                        self.toolTip.showText(event.globalPos(),buttons[i],msecShowTime = 2000)
                    return
                
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # left mouse pressed
    def leftMouse(self,e):
        # position is QPointf here! Must convert to QPoint to compare to rect
        pos = e.position()
        x = pos.x(); y = pos.y()
        point = QPoint(x,y)
            
        # if none of these happen, then drag with the mouse
        save = self.pressPos
        self.pressPos = None
        if self.tuningKnobRect.contains(point):
            self.tuningKnob()
        elif self.symbolRect.contains(point):
            self.symbol()
        elif self.tunerRect.contains(point):
            self.tuner(point)
        else:
            for i in range(len(self.buttonRects)):
                if self.buttonRects[i].contains(point):
                    self.radioButton(i)
                    return
        # restore pressPos for dragging
        self.pressPos = save

#  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    import os
                    
    import sys
    app = QApplication(sys.argv)
    win = MyBorderLessWindow()
    win.show()
    sys.exit(app.exec())
