#
# This was generated by chatGPT to find the rectangles on an
# image. The x,y values must have 10 added to them for some
# unknown reason
#
# If the image needs cropped, do that before running this
#
import sys
from PySide6.QtCore import Qt, QRectF,QRect,QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QGraphicsRectItem, QGraphicsPixmapItem,
                               QWidget,QRubberBand)

class ImageOutlineApp(QApplication):
    def __init__(self, argv):
        super(ImageOutlineApp, self).__init__(argv)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setWindowTitle("Image Outline")
        self.view.setRenderHint(QPainter.Antialiasing)

        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        self.rectangle_item = QGraphicsRectItem()
        self.scene.addItem(self.rectangle_item)

        # Load image
        image_path = "images/radio1.png"
        if len(argv) > 1:
            image_path = argv[1]
        self.load_image(image_path)

        self.view.show()
        self.start_point = None

        self.view.mousePressEvent = self.mouse_press_event
        self.view.mouseMoveEvent = self.mouse_move_event
        self.view.mouseReleaseEvent = self.mouse_release_event
        self.view.keyPressEvent = self.keyPressEvent
        
    def load_image(self, path):
        pixmap = QPixmap(path)
        self.image_item.setPixmap(pixmap)
        w = pixmap.width()
        h = pixmap.height()
        self.view.resize(w, h)
        
    def keyPressEvent (self,event):
        if event.key() == Qt.Key_Escape:
            self.exit(0)

    def mouse_press_event(self, event):
        self.start_point = event.position()
        print(self.start_point)
        self.rectangle_item.setRect(QRectF(self.start_point, self.start_point))

    def mouse_move_event(self, event):
        if self.start_point is not None:
            current_rect = QRectF(self.start_point, event.position())
            self.rectangle_item.setRect(current_rect.normalized())

    def mouse_release_event(self, event):
        if self.start_point is not None:
            rect = QRectF(self.start_point, event.position())
            self.rectangle_item.setRect(rect.normalized())
            self.start_point = None
            # convert to integer, have to add 10 for
            # some unknown reason
            x = int(rect.x()) + 10
            y = int(rect.y()) + 10
            w = int(rect.width()); h = int(rect.height())
            print(f"Rectangle {x},{y},{w},{h}")

if __name__ == "__main__":
    app = ImageOutlineApp(sys.argv)
    sys.exit(app.exec())
