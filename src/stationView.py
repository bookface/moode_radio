#-*- coding: utf-8 -*-
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

from PySide6.QtCore import (Signal,QItemSelectionModel)
from PySide6.QtWidgets import QMainWindow, QListWidget,QMessageBox

import subprocess
import os
if os.name == 'nt':
    from subprocess import CREATE_NO_WINDOW

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Reads list of stations from station_data.json file downloaded via Backup
# from Moode.  Returns url of selected station
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
import sys
import json
import io

class StationView(QMainWindow):
    # signals must be declared before init
    selected = Signal()
    closed   = Signal(int)
    
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def __init__(self,currentRow,moode,parent=None):
        super().__init__(parent)

        self.moode_url = moode
        
        self.list = QListWidget(self)
        self.list.itemClicked.connect(self.clicked)
        self.list.setSortingEnabled(True)

        # old version used the json file downloaded from moode.
        # this version downloads the pls names using mpc
        self.useMPC = True
        if self.useMPC:
            self.load_from_mpc()
        else:
            self.load_from_station_data()
        
        self.resize(400,500)
        self.setWindowTitle("Station List")
        self.setCentralWidget(self.list)
        self.url = None         # return value
        self.name = None        # return value

        # move to the last selected row instead of always going to
        # the top of the list
        self.list.setCurrentRow(currentRow,QItemSelectionModel.SelectCurrent)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # talk to moode using mpc
    def cmd(self,which):
        proc = f"mpc --quiet -h {self.moode_url} {which}"
        try:
            ps = subprocess.run(proc, shell=True, capture_output=True,text=True,check=True,timeout=3)
            return ps.stdout
        except:
            self.errorMessage()
        return ''

    def errorMessage(self):
        QMessageBox.warning(self,
                            "Station View",
                            f"Cant make contact with {self.moode_url} to\nRetrieve the Station List",
                            QMessageBox.Ok)
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # download the list of radio stations (.pls files) using mpc
    def load_from_mpc(self):
        output = self.cmd('ls RADIO')
        for line in output.splitlines():
            line = line.replace('RADIO/', "", 1) # for easier reading
            self.list.addItem(line) # add to qlistwidget

                
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # deprecated - loads from the json file 'station_data.json'
    # downloaded using moode backup
    def load_from_station_data(self):
        # urls are saved in a dictionary, indexed by
        # the station name. Hopefully, there are no
        # duplicate station names.
        self.urls = {}

        # Add items to the list and urls
        json_file = 'station_data.json'
        with open(json_file) as json_data:
            data = json.load(json_data) # returns a python dictionary
            for station in data['stations']:
                name = station['name']
                url  = station['station']
                self.list.addItem(name) # add to qlistwidget
                self.urls[name] = url   # add to url dictionary
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # close the list and return the current selected row
    def closeEvent(self,e):
        row = self.list.currentRow()
        self.closed.emit(row)
        self.close()
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # Item clicked. Set 'self.url' to the selected url, and emit
    # 'selected'. Keep list showing.
    def clicked(self,item):
        row = self.list.currentRow() # current selected row
        item = self.list.item(row)   # item in the row
        self.name = item.text()      # get the name
        if self.useMPC:
            self.url = None
        else:
            self.url = self.urls[self.name] # get the url
        self.selected.emit()
        
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# just for testing
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StationView(0,moode='192.168.1.2')
    window.show()
    sys.exit(app.exec())
