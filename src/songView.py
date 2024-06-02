# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
# This loads a list of files on the system and requests moode
# to play either the song or the directory.
#
# Change rootDirectory() to point to your root directory, the
# url moode, and the mounted name on the raspberry pi.
#
# TODO: Put the system dependant stuff in an ini
#       file.
#       Popup menu code doesn't do anything
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
import sys
from PySide6.QtCore import QDir, Qt
from PySide6.QtWidgets import (QApplication, QMainWindow,
                               QTreeView, QVBoxLayout, QHBoxLayout,QWidget,
                               QAbstractItemView, QMenu,QPushButton,
                               QFileSystemModel, QFrame)
from PySide6.QtGui import (QCursor,QAction)

import os
import subprocess
import glob
from pathlib import Path
import getpass

if os.name == 'nt':
    from subprocess import CREATE_NO_WINDOW

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# System dependances here:
#
# Return the local mount music directory,the url of the moode player,
# and the name of the directory on moode where the music is mounted
#
# For example, the directory on moode is samba exported as 'music',
# mounted here as /media/{user}/music or X:/Music
#
def rootDirectory():
    url  = 'moode.local'
    if os.name == 'nt':
        root = 'X:/Music'
        url  = '192.168.1.2'    # windows can't handle moode.local
    else:
        user = getpass.getuser()
        #root = f"/media/{user}/easystore/Music"
        root = f"/media/{user}/music"
    #
    # mounted name on moode, e.g. /media/<name> WITHOUT /media
    #
    mounted_name = 'easystore'
    return root,url,mounted_name

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class DirectoryTreeApp(QMainWindow):

    # run an mpc command
    def cmd(self,which):
        proc = f"mpc --quiet -h {self.url} {which}"
        try:
            if os.name == 'nt':
                subprocess.run(proc,creationflags=CREATE_NO_WINDOW,timeout = 3)
            else:
                subprocess.run(proc,shell=True,timeout = 3)
        except subprocess.TimeoutExpired:
            print(f"MPC Error, check URL:{self.url}")
        
    #
    # run an mpc command and get something back
    # not used right now
    # could be used to play the last item in the play list
    #   result = self.cmdResult('playlist')
    #   last = len(result) + 1
    #   self.cmd(f"play {last}")
    #
    def cmdResult(self,which):
        import signal
        result = []
        proc = f"mpc -h {self.url} {which}"
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
    # transform from local path to raspberry pi path
    def fixPath(self,path):
        p = path.replace("\\", "/") # replace windows annoying back slashes
        p2 = p.replace(self.root,self.mountName)
        return p2

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # add an action to a popup menu
    def addAction(self,name,popup,callback):
        a = QAction(name, self)
        popup.addAction(a)
        a.triggered.connect(callback)

    # add file or directory to playlist
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
                print("************** ADD HERE",filename)
                self.cmd(f"add \"{filename}\"")
        else:                   # one file
            filename = self.fixPath(path)
            self.cmd(f"add \"{filename}\"")

        self.selectedPath = ''

    # toggle play/pause
    def play(self):
        self.cmd('toggle')
        return

    # clear playlist before adding
    def clearAdd(self):
        self.cmd('clear')
        self.add()
        self.cmd('play 1')
        
    def cancel(self):
        pass
    
    def previous(self):
        self.cmd('prev')

    def nextsong(self):
        self.cmd('next')

    # popup menu
    def popupMenu(self,point):
        popup = QMenu(self)
        popup.setStyleSheet('background-color: white; selection-color:red; font-size: 20px ')
        self.addAction('Add',popup,self.add)
        self.addAction('Clear and Add',popup,self.clearAdd)
        self.addAction('Cancel',popup,self.cancel)
        popup.exec(point)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def __init__(self):
        super().__init__()

        self.root,self.url,self.mountName = rootDirectory()

        self.setWindowTitle(f"Music Selector {self.root}")
        self.setGeometry(100, 100, 800, 1000)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.frame = QFrame(self)
        hlayout = QHBoxLayout(self.frame)
        self.pb = QPushButton(self)
        self.pb.setText("PLAY / PAUSE")
        self.pb.clicked.connect(self.play)
        hlayout.addWidget(self.pb)
        self.prev = QPushButton(self)
        self.prev.setText("PREV")
        self.prev.clicked.connect(self.previous)
        hlayout.addWidget(self.prev)

        self.next = QPushButton(self)
        self.next.setText("NEXT")
        self.next.clicked.connect(self.nextsong)
        hlayout.addWidget(self.next)
        self.layout.addWidget(self.frame)

        self.frame2 = QFrame(self)
        hlayout = QHBoxLayout(self.frame2)
        self.addto = QPushButton(self)
        self.addto.setText("ADD")
        self.addto.clicked.connect(self.add)
        hlayout.addWidget(self.addto)
        self.clearaddto = QPushButton(self)
        self.clearaddto.setText("CLEAR/ADD/PLAY")
        self.clearaddto.clicked.connect(self.clearAdd)
        hlayout.addWidget(self.clearaddto)
        self.playlocal = QPushButton(self)
        self.playlocal.setText("PLAY LOCAL")
        self.playlocal.clicked.connect(self.player)
        hlayout.addWidget(self.playlocal)
        self.layout.addWidget(self.frame2)


        self.selectedPath = ''
        self.treeView = QTreeView(self)
        self.treeView.setSelectionMode(QTreeView.SingleSelection)
        self.treeView.setSelectionBehavior(QTreeView.SelectRows)
        self.treeView.clicked.connect(self.display_selectedPath)
        self.layout.addWidget(self.treeView)

        # Create a QFileSystemModel to represent the file system
        self.fileSystemModel = self.create_fileSystemModel()
        self.treeView.setModel(self.fileSystemModel)
        self.treeView.setRootIndex(self.fileSystemModel.index(self.root))
        self.treeView.setColumnWidth(0,400)

        
    def display_selectedPath(self, index):
        self.selectedPath = self.fileSystemModel.filePath(index)
        return
        point = QCursor.pos()
        point.setY(point.y()- 25)
        self.popupMenu(point)
        
    def create_fileSystemModel(self):
        model = QFileSystemModel()
        model.setRootPath(QDir.rootPath())
        # model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Drives)
        return model

    # play a file here
    def player(self):
        if self.selectedPath == '': return
        path = self.selectedPath
        if os.path.isdir(path): # only files play for now
            return
        filename = self.fixPath(path)
        filename = filename.replace(self.mountName,self.root)
        if os.name == 'nt':
            import subprocess
            subprocess.Popen(["pythonw","player.py",filename])
        else:                   # linux
            subprocess.Popen(["python3","player.py",filename])
        
def main():
    app = QApplication(sys.argv)
    window = DirectoryTreeApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

