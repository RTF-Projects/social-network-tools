from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from app.widgets.tab_widget.tab_widget import TabWidget


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_styles()

        self.tab_widget = TabWidget(self)

        self.show()


    def setup_styles(self):
        self.setWindowTitle('Social Cleaner') #название окна

        self.setStyleSheet("background-color: #D6DEE8;")  # цвет фона

        self.setWindowIcon(QIcon('./app/styles/sc_logo.png')) #иконка

        stylesheet = self.load_stylesheet("./app/styles/styles.qss")
        self.setStyleSheet(stylesheet)

    @staticmethod
    def load_stylesheet(filename):
        with open(filename, "r") as f:
            return f.read()


