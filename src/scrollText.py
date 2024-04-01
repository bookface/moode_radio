from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget, QScrollBar
from PySide6.QtCore import Qt, QTimer

class ScrollableTextEdit(QMainWindow):
    def __init__(self):
        super(ScrollableTextEdit, self).__init__()

        self.setWindowTitle("Scrollable Text Edit")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create a QPlainTextEdit widget
        self.text_edit = QPlainTextEdit(self)
        layout.addWidget(self.text_edit)

        # Set some long text for demonstration
        long_text = "This is a long line of text that will scroll back and forth. " #  * 10
        self.text_edit.setPlainText(long_text)

        # Set up horizontal scrolling
        self.setup_horizontal_scrolling()

    def setup_horizontal_scrolling(self):
        # Create a timer to scroll the text horizontally
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_text_horizontally)
        self.scroll_timer.start(50)  # Adjust the interval based on your preference

    def scroll_text_horizontally(self):
        # Scroll the text horizontally by moving the horizontal scrollbar
        scroll_bar = self.text_edit.horizontalScrollBar()
        current_value = scroll_bar.value()
        maximum_value = scroll_bar.maximum()
        print("scroll",current_value,maximum_value)

        # Reverse the scrolling direction when reaching the edges
        if current_value == 0:
            scroll_bar.setValue(maximum_value)
        else:
            scroll_bar.setValue(current_value - 1)

if __name__ == "__main__":
    app = QApplication([])
    window = ScrollableTextEdit()
    window.show()
    app.exec()
