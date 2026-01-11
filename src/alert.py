#-*- coding: utf-8 -*-
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# TPS Server has a alert message display, but this class is used
# to indicate that the Server is not running or there is a problem
# communicating with it

from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import  QDialog, QWidget, QLabel,QVBoxLayout
from PySide6.QtGui import QFont

def screen_width():
    import tkinter as tk
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    root.destroy()
    return screen_width

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class AlertDialog(QDialog):

    def __init__(self,message,red = True, duration = 3000, fade = True):
        super().__init__()
        self.message = message
        self.duration = duration
        self.red = red
        self.fade = fade
        self.exitWhenDone = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        if self.red == True:
            background = 'background-color: rgb(255,0,0)'
        elif self.red == None:
            background = 'background-color: rgb(255,255,0)'
        else:
            background = 'background-color: rgb(0,255,0)'

        self.setStyleSheet(background)
        self.setWindowTitle('ALERT')

        w = screen_width()
        self.resize(w,50)
        # bottom move(0,rect.height - 50)
        self.move(0,0)
        self.label = QLabel(self)
        # size, weight, italic
        font = QFont('Arial',25,-1,False)
        self.label.setFont(font)
        self.label.setText(message)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label, 0, Qt.AlignHCenter) # Qt.AlignCenter)
        
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(self.beginExit)
        t.start(self.duration)
        self.show()

    def closeThisDialog(self):
        if self.exitWhenDone:
            QApplication.closeAllWindows()
            QApplication.quit()
        else:
            self.close()

    def fader(self):
        self.opacity -= 0.01
        self.setWindowOpacity(self.opacity)
        if self.opacity <= 0.0:
            self.timer.stop()
            self.closeThisDialog()

    def beginExit(self):
        self.opacity = 1.0
        if self.fade == True:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.fader)
            self.timer.start(30)
        else:
            self.closeThisDialog()

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    msg = 'alert test'
    dur = 2000
    red = False
    if len(sys.argv) > 1:
        msg = sys.argv[1]
        if len(sys.argv) > 2:
            dur = int(sys.argv[2])
        if len(sys.argv) > 3:
            red = True

    a = AlertDialog(msg,red=red,fade = True, duration = 2000)
    app.exec()
