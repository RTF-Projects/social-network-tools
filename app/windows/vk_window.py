from PyQt5.QtWidgets import QWidget
from qasync import asyncSlot, asyncClose


class VKWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window

        self.configure_elements()
        self.set_texts()

    def set_texts(self):
        pass

    def configure_elements(self):
        pass

    @asyncSlot()
    async def pass_func(self):
        pass

    @asyncClose
    async def closeEvent(self, event):
        pass
