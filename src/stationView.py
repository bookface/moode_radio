
from PySide6.QtCore import (Signal,QItemSelectionModel)

from PySide6.QtWidgets import QMainWindow, QListWidget

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# Reads list of stations from station_data.json file downloaded via Backup
# from Moode.  Returns url of selected station
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
import sys
import json

class StationView(QMainWindow):
    # signals must be declared before init
    selected = Signal()
    closed   = Signal(int)
    
    def __init__(self,currentRow,parent=None):
        super().__init__(parent)

        self.list = QListWidget(self)
        self.list.itemClicked.connect(self.clicked)
        self.list.setSortingEnabled(True)

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
        self.resize(400,500)
        self.setWindowTitle("Station List")
        self.setCentralWidget(self.list)
        self.url = None
        self.name = None

        # move to the last selected row instead of always going to
        # the top of the list
        self.list.setCurrentRow(currentRow,QItemSelectionModel.SelectCurrent)
        
    # close the list and return the current selected row
    def closeEvent(self,e):
        row = self.list.currentRow()
        self.closed.emit(row)
        self.close()
        
    # Item clicked. Set 'self.url' to the selected url, and emit
    # 'selected'. Keep list showing.
    def clicked(self,item):
        row = self.list.currentRow() # current selected row
        item = self.list.item(row)   # item in the row
        self.name = item.text()      # get the name
        self.url = self.urls[self.name] # get the url
        self.selected.emit()
        
# just for testing
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StationView(0)
    window.show()
    sys.exit(app.exec())
