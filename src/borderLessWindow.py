from PySide6.QtCore import (Qt, QPoint, QPointF, QSize, QEvent)
from PySide6.QtWidgets import (QMainWindow,QWidget,QFrame,
                               QLabel,QSizePolicy,QVBoxLayout,
                               QRubberBand,QMessageBox)
from PySide6.QtGui import (QPalette,QImage,QPixmap)

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# A Widgets that overlays rectangles, for debugging mouse press areas
#
class RubberBandWidget(QWidget):

    def __init__(self,parent = None):
        super().__init__(parent)
        self.rubberBands = []
        self.hidden = True

    def addRectangle(self,rect):
        rubberBand = QRubberBand(QRubberBand.Line, self)
        rubberBand.setGeometry(rect)
        self.rubberBands.append(rubberBand)

    def delete(self):
        for rubberBand in self.rubberBands:
            rubberBand.deleteLater()
        self.rubberBands.clear()
        
    def hide(self):
        for rubberBand in self.rubberBands:
            rubberBand.hide()
            self.hidden = True

    def show(self):
        for rubberBand in self.rubberBands:
            rubberBand.show()
            self.hidden = False

    def toggle(self):
        if self.hidden:
            self.show()
        else:
            self.hide()
        
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# A QMainwindow with an image
# The default scale is just the size of the image file.  It can be scaled
# by applying a scale parameter
#
class BorderLessWindow(QMainWindow):

    def __init__(self,image,scale = 1.0):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pressPos = None    # used to drag with the mouse
        self.useRight = False
        self.resize(800,600)

        central_widget = RubberBandWidget(self)
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

        self.loadImageAndScale(image,scale)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def loadImageAndScale(self,image,scale):
        self.scale = scale
        self.loadImage(image)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # ToolTip is returned when hovering, QHoverEvent doesn't register
    def eventFilter(self, object, event):
        # got to be a better way
        s = str(event)
        if "QEvent::ToolTip" in s:
            self.hover(event)
        return False

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
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
        sz = QSize(w, h)
        if self.scale != 1.0:
            sz = QSize(w * self.scale, h*self.scale)
        self.resize(sz)

        aspect = Qt.KeepAspectRatio # or Qt.IgnoreAspectRatio
        self.pixmap = self.pixmap.scaled(sz,aspect,Qt.SmoothTransformation)
        self.imageLabel.setPixmap(self.pixmap)

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def hover(self,event):      # overide this
        pass
    def rightMouse(self):       # override this
        pass
    def leftMouse(self,e):      # override this
        pass
    
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # record the position of the mouse when a button is pressed
    def mousePressEvent(self,event):
        self.pressPos = event.position() # save initial drag position
        print("borderlesss",event.position())
        if event.button() == Qt.RightButton:
            self.rightMouse()
        elif event.button() == Qt.LeftButton:
            self.leftMouse(event)
        else:
            self.pressPos = None # middle mouse?


    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    def mouseMoveEvent(self, event):
        x=event.globalPosition().x()
        y=event.globalPosition().y()
        if self.pressPos != None:
            self.move(x-self.pressPos.x(), y-self.pressPos.y())
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # record ctrl and alt (not used yet)
    def keyReleaseEvent(self,event):
        if event.key() == Qt.Key_Escape:
            self.close()
        self.ctrl = False
        self.alt = False
        
    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # only keys used are Escape to exit and "t" to toggle
    # the overlays
    def keyPressEvent (self,event):
        # sometimes works, sometimes doesn't: see keyReleaseEvent
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_T:
            self.toggleOverlays()
            
        m = event.modifiers()
        if m == Qt.ControlModifier:
            self.ctrl = True
        elif m == Qt.AltModifier:
            self.alt = True
        # print("ALT",self.alt,"CTRL",self.ctrl)
        
