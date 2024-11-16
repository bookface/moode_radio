# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
import os
#import subprocess
import glob
from pathlib import Path
import getpass

# Looks like subprocess is not very portable. Windows requires the
# CREATE_NO_WINDOW parameter
import subprocess
if os.name == 'nt':
    from subprocess import CREATE_NO_WINDOW

from PySide6.QtCore import (Qt, QPoint, QPointF, QSize, QEvent, QDir,
                            QRect, QTimer, Signal, QSettings)
from PySide6.QtWidgets import (QApplication, QMainWindow,QStyle,
                               QTreeView, QTreeWidget,QVBoxLayout, QHBoxLayout,QWidget,
                               QGridLayout,QAbstractItemView, QMenu,QPushButton,
                               QFileSystemModel, QFrame, QSlider)
from PySide6.QtGui import (QPixmap,QImage,QHoverEvent, QBrush,
                           QPen,QFont,QTransform,QCursor,QAction,
                           QIcon,QMovie)

from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QItemSelectionModel
# from PySide6.QtWidgets.QStyle import SP_MediaPause

from roundCorners import makeCornersRound
from turntableWindow import BorderLessWindow,RubberBandWidget
from clickableLabel import ClickableLabel

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def rootDirectory():
    url  = 'moode.local'
    if os.name == 'nt':
        root = 'X:/Music'
        url  = '192.168.12.179'    # windows can't handle moode.local
    else:
        # mount the directory containing files
        root = f"/media/easystore/Music"
    #
    # The mounted name of music files on the raspberry pi,
    # e.g. /media/<name> WITHOUT /media
    #
    mounted_name = 'easystore'
    return root,url,mounted_name

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# run an mpc command
def mpc_cmd(which):
    root,url,mount = rootDirectory()
    proc = f"mpc --quiet -h {url} {which}"
    try:
        if os.name == 'nt':
            subprocess.run(proc,creationflags=CREATE_NO_WINDOW,timeout = 3)
        else:
            subprocess.run(proc,shell=True,timeout = 3)
    except subprocess.TimeoutExpired:
        print(f"MPC Error, check URL:{url}")
        
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# run an mpc command and get something back
#
def mpc_cmdResult(which):
    import signal
    result = []
    root,url,mount = rootDirectory()
    proc = f"mpc -h {url} {which}"
    print("proc",proc)
    try:
        process = subprocess.Popen(proc,shell=True,
                                   stdin=None,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait(timeout=1)
        result=process.stdout.readlines()
    except subprocess.TimeoutExpired:
        # self.label.setText(f"Error In Communication, check URL:{url}")
        print(f"Error In Communication, check URL:{url}")
        os.kill(process.pid, signal.SIGTERM)
        
    return result

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class MyTreeView(QTreeView):
    selected = Signal() # QModelIndex)
    
    def __init__(self,parent=None):
        super().__init__(parent)

    def mousePressEvent(self,e):
        print("MOUSE PRESS",e.button())
        if e.button() == Qt.MouseButton.LeftButton:
            index = self.currentIndex()
            #self.selected.emit() # index)
            #selectionModel = self.selectionModel()
            #selectionModel.select(index,QItemSelectionModel.Select)
            self.setCurrentIndex(index)
            #self.currentChanged(index,index)
            #self.setCurrentIndex(index)
            #super().clicked.emit(index)
            print("left")
            #item = self.model.itemFromIndex(index) # .setBackground(Qt.yellow)
            #e.ignore()
        elif e.button() == Qt.MouseButton.RightButton:
            index = self.currentIndex()
            self.setCurrentIndex(index)
            self.selected.emit() # index)
            print("Right Button")
        super().mousePressEvent(e)
        
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class MainWindow(BorderLessWindow):

    def __init__(self):
        super().__init__('images/turntable.png',scale=0.8,hbox=True)
        self.root,self.url,self.mountName = rootDirectory()
        self.movieRunning = False

        self.movie = QMovie("images/turntable.gif")
        
        self.filetree()
        self.resize(self.imageWidth * 2.0,self.height())
        self.selectedPath = ''

        self.status()

    def status(self):
        result = mpc_cmdResult('')
        if len(result) > 1:
            stat = result[1].decode('utf-8')
            stat = stat[1:5]
        else:
            stat = 'paus'
        if stat == 'paus':
            self.paused = True
            self.stopMovie()
        else:
            self.pause = False
            self.startMovie()
            
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def rightMouse(self,point):
        index = self.treeView.indexAt(point)
        if (index.isValid() and index.row() % 2 == 0):
            self.popupMenu(point)
        return
    
        # position is QPointf here! Must convert to QPoint to compare to rect
        pos = e.position()
        x = pos.x(); y = pos.y()
        point = QPoint(x,y)
        print("POPUP UPD")
        self.popupMenu()

    # popup menu
    def addAction(self,name,popup,callback):
        a = QAction(name, self)
        popup.addAction(a)
        a.triggered.connect(callback)

    def popupMenu(self):
        popup = QMenu(self)
        popup.setStyleSheet('background-color: white; selection-color:red; font-size: 20px ')
        self.addAction('Add',popup,self.add)
        self.addAction('Clear and Add',popup,self.clearAdd)
        self.addAction('Cancel',popup,self.cancel)

        p = QCursor.pos()
        point = QPoint(p.x(),p.y())
        popup.exec(point)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # add file or directory to playlist
    # clear playlist before adding
    def clearAdd(self):
        mpc_cmd('clear')
        self.add()
        mpc_cmd('play 1')
        self.status()
        
    def cancel(self):
        pass

    # toggle play/pause
    def play(self):
        mpc_cmd('toggle')
        self.status()

    def previous(self):
        mpc_cmd('prev')

    def nextsong(self):
        mpc_cmd('next')

    def player(self):
        pass

    def volume(self):
        mpc_cmd(f'vol {self.slider.value()}')
    
    def fixPath(self,path):
        p = path.replace("\\", "/") # replace windows annoying back slashes
        p2 = p.replace(self.root,self.mountName)
        return p2

    def add(self):
        if self.selectedPath == '':
            print("no path")
            return

        path = self.selectedPath
        if os.path.isdir(path):
            # sort then add all files
            list = [str(child.resolve()) for child in Path.iterdir(Path(path))]
            list = sorted(list)
            for f in list:
                filename = self.fixPath(f)
                mpc_cmd(f"add \"{filename}\"")
        else:                   # one file
            filename = self.fixPath(path)
            mpc_cmd(f"add \"{filename}\"")

        self.selectedPath = ''
        self.status()


    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def startMovie(self):
        if self.movieRunning == False:
            self.movieRunning = True
            self.imageLabel.setPixmap(QPixmap())
            self.imageLabel.setMovie(self.movie)
            size = self.imageLabel.size()
            self.movie.setScaledSize(size)
            self.movie.start()
            
    def stopMovie(self):
        if self.movieRunning:
            self.movieRunning = False
            self.movie.stop()
        
    def toggleMovie(self):
        if self.movieRunning == False:
            self.startMovie()
        else:
            self.stopMovie()
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def filetree(self):

        widget = QWidget(self)
        self.layout.addWidget(widget)
        vlayout = QGridLayout()
        widget.setLayout(vlayout)

        self.frame = QFrame()
        vlayout.addWidget(self.frame)
        hlayout = QHBoxLayout(self.frame)
        self.pb = QPushButton()

        # self.pb.setText("PLAY / PAUSE")
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.pb.setIcon(icon)
        self.pb.clicked.connect(self.play)
        hlayout.addWidget(self.pb)

        self.prev = QPushButton()
        #self.prev.setText("PREV")
        icon = self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        self.prev.setIcon(icon)
        self.prev.clicked.connect(self.previous)
        hlayout.addWidget(self.prev)

        self.next = QPushButton()
        #self.next.setText("NEXT")
        icon = self.style().standardIcon(QStyle.SP_MediaSeekForward)
        self.next.setIcon(icon)
        self.next.clicked.connect(self.nextsong)
        hlayout.addWidget(self.next)

        self.addto = QPushButton()
        self.addto.setText("+")
        self.addto.clicked.connect(self.add)
        hlayout.addWidget(self.addto)

        self.clearaddto = QPushButton()
        self.clearaddto.setText("CLEAR+")
        self.clearaddto.clicked.connect(self.clearAdd)
        hlayout.addWidget(self.clearaddto)

        if False:
            self.frame2 = QFrame()
            vlayout.addWidget(self.frame2)
            hlayout = QHBoxLayout(self.frame2)

            self.playlocal = QPushButton()
            self.playlocal.setText("PLAY LOCAL")
            self.playlocal.clicked.connect(self.player)
            hlayout.addWidget(self.playlocal)

        # volume slider
        self.frame3 = QFrame()
        vlayout.addWidget(self.frame3)
        hlayout = QHBoxLayout(self.frame3)
        self.slider = QSlider(Qt.Horizontal,self.frame3)
        self.slider.setMaximum(100)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(2)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.valueChanged.connect(self.volume)
        hlayout.addWidget(self.slider)

        self.treeView = QTreeView()
        vlayout.addWidget(self.treeView)
        #self.treeView.selected.connect(self.popupMenu)
        self.treeView.setSelectionMode(QTreeView.SingleSelection)
        self.treeView.setSelectionBehavior(QTreeView.SelectRows)
        self.treeView.clicked.connect(self.display_selectedPath)

        # Create a QFileSystemModel to represent the file system
        self.fileSystemModel = self.create_fileSystemModel()
        self.treeView.setModel(self.fileSystemModel)
        self.treeView.setRootIndex(self.fileSystemModel.index(self.root))
        self.treeView.setColumnWidth(0,400)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def display_selectedPath(self, index):
        self.selectedPath = self.fileSystemModel.filePath(index)
        print("PATH SELECTED",self.selectedPath)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def create_fileSystemModel(self):
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())
        # model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Drives)
        return model
        
#  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    import os

    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
