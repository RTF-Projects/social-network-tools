import asyncio

import aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton
from app.const import BUTTON_HEIGHT
from app.locales.locales import locales
from qasync import asyncSlot, asyncClose


class TelegramWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window

        self.leave_chat_button = QPushButton(self)

        self.configure_elements()
        self.set_texts()

    @asyncSlot()
    async def leave_chat(self):
        pass

    @asyncClose
    async def closeEvent(self, event):
        pass

    def set_texts(self):
        self.leave_chat_button.setText(locales[self.settings_window.locale]['leave_chat'])

    def configure_elements(self) -> None:
        self.leave_chat_button.clicked.connect(self.leave_chat)
        self.leave_chat_button.setFixedHeight(BUTTON_HEIGHT)

