import sys
from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QLineEdit,
    QMainWindow, QPushButton, QToolBar)
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):

    def __init__(self,url):
        super().__init__()

        self.addToolbar()

        self.webEngineView = QWebEngineView()
        self.setCentralWidget(self.webEngineView)
        self.addressLineEdit.setText(url)
        self.webEngineView.load(QUrl(url))
        self.webEngineView.page().titleChanged.connect(self.setWindowTitle)
        self.webEngineView.page().urlChanged.connect(self.urlChanged)


    def addToolbar(self):
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        self.backButton = QPushButton()
        self.backButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/left-32.png'))
        self.backButton.clicked.connect(self.back)
        self.toolBar.addWidget(self.backButton)
        self.forwardButton = QPushButton()
        self.forwardButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/right-32.png'))
        self.forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(self.forwardButton)

        self.addressLineEdit = QLineEdit()
        self.addressLineEdit.returnPressed.connect(self.load)
        self.toolBar.addWidget(self.addressLineEdit)

        
    @Slot()
    def load(self):
        url = QUrl.fromUserInput(self.addressLineEdit.text())
        if url.isValid():
            self.webEngineView.load(url)

    @Slot()
    def back(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Back)

    @Slot()
    def forward(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Forward)

    @Slot(QUrl)
    def urlChanged(self, url):
        self.addressLineEdit.setText(url.toString())


if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    app = QApplication(sys.argv)
    url = 'http://192.168.10.67'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    mainWin = MainWindow(url)
    # availableGeometry = mainWin.screen().availableGeometry()
    # mainWin.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3)
    mainWin.resize(1000,600)
    mainWin.show()
    sys.exit(app.exec())
