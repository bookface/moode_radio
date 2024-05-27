import sys
from PySide6.QtCore import QUrl, Qt,QRect
from PySide6.QtGui import QIcon,QTransform
from PySide6.QtWidgets import (QApplication, QLineEdit,QMessageBox,
    QMainWindow, QPushButton, QToolBar)
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from borderLessWindow import BorderLessWindow
# Rectangle 141,151,851,301

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class MainWindow(BorderLessWindow):
    def __init__(self,url):
        self.webRect = QRect(141,151,851,301)
        scale = 0.75
        self.scaleRectangle(scale)
        super().__init__('images/radio7.png',scale)
        self.webEngineView = QWebEngineView(self)
        self.webEngineView.setGeometry(self.webRect)
        self.webEngineView.move(self.webRect.x(),self.webRect.y())
        self.webEngineView.load(QUrl(url))

    def scaleRectangle(self,scale):
        if scale != 1.0:
            transform = QTransform()
            transform = transform.scale(scale,scale)
            self.webRect = transform.mapRect(self.webRect)

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    app = QApplication(sys.argv)
    url = 'http://192.168.1.2'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    mainWin = MainWindow(url)
    # availableGeometry = mainWin.screen().availableGeometry()
    # mainWin.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3)
    mainWin.resize(1000,600)
    mainWin.show()
    sys.exit(app.exec())
