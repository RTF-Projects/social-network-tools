import asyncio
from datetime import datetime, timedelta

import aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton
from qasync import asyncSlot, asyncClose
from telethon import TelegramClient

from app.const import BUTTON_HEIGHT
from app.locales.locales import locales


class TelegramWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window

        self.days_to_leave = 30
        self.days_to_stop_search = 50
        self.client = TelegramClient(self.settings_window.session_name_telegram,
                                     self.settings_window.token_telegram,
                                     self.settings_window.token_hash_telegram,
                                     system_version=self.settings_window.system_version_telegram)

        self.leave_chat_button = QPushButton(self)

        self.configure_elements()
        self.set_texts()

    @asyncSlot()
    async def leave_chat(self):
        await self.client.start()

        me = await self.client.get_me()
        my_id = me.id
        groups_to_leave = []
        groups = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.id)

        for group in [1002141563035]:
            group_entity = await self.client.get_entity(group)
            async for message in self.client.iter_messages(group_entity):
                if message.date.timestamp() < (datetime.today() - timedelta(days=self.days_to_stop_search)).timestamp():
                    break
                if message.sender_id == my_id:
                    if message.date.timestamp() > (datetime.today() - timedelta(days=self.days_to_leave)).timestamp():
                        break
                    else:
                        groups_to_leave.append(group)
                        break

        print(groups_to_leave)

    @asyncSlot()
    async def leave_chat_unread(self):
        await self.client.start()

        groups_to_leave = []
        groups = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group and dialog.dialog.unread_count > 0:
                groups.append([dialog.id, dialog.dialog.read_inbox_max_id])

        for group in groups[:1]:
            group_entity = await self.client.get_entity(group[0])
            async for message in self.client.iter_messages(group_entity, offset_id=group[1]):
                groups_to_leave.append([group[0], message.date])
                break

        print(groups_to_leave)

    @asyncClose
    async def closeEvent(self, event):
        pass

    def set_texts(self):
        self.leave_chat_button.setText(locales[self.settings_window.locale]['leave_chat'])

    def configure_elements(self) -> None:
        self.leave_chat_button.clicked.connect(self.leave_chat)
        self.leave_chat_button.setFixedHeight(BUTTON_HEIGHT)

