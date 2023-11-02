
from PySide6.QtCore import (Signal)
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
    
    def __init__(self,parent=None):
        super().__init__(parent)

        self.list = QListWidget(self)
        self.list.itemClicked.connect(self.clicked)
        self.urls = []
        # Add items to the list
        json_file = 'station_data.json'
        with open(json_file) as json_data:
            data = json.load(json_data) # returns a python dictionary
            for station in data['stations']:
                self.list.addItem(station['name']) # ,station['station'])
                self.urls.append(station['station'])
        self.resize(400,500)
        self.setWindowTitle("Station List")
        self.setCentralWidget(self.list)
        self.url = None
        self.name = None
        
    # Item clicked. Set 'self.url' to the selected url, and emit
    # 'selected'
    def clicked(self,item):
        row = self.list.currentRow()
        item = self.list.item(row)
        self.name = item.text()
        self.url = self.urls[row]
        self.selected.emit()
        
# just for testing
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StationView()
    window.show()
    sys.exit(app.exec())
