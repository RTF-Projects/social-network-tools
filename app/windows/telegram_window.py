import asyncio
from datetime import datetime, timedelta

import aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidgetItem, QListWidget
from qasync import asyncSlot, asyncClose
from telethon import TelegramClient
from telethon.tl.types import Channel

from app.const import BUTTON_HEIGHT
from app.entities.group import Group
from app.entities.user import User
from app.locales.locales import locales
from app.widgets.list_adapter_widget.double_list_adapter_widget import DoubleListAdapter


#TODO int masks; delete and delete all buttons; objects count (remove :10); search filter?


class TelegramWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window

        self.client = TelegramClient(self.settings_window.session_name_telegram,
                                     self.settings_window.token_telegram,
                                     self.settings_window.token_hash_telegram,
                                     system_version=self.settings_window.system_version_telegram)

        self.find_readonly_chats_button = QPushButton(self)
        self.readonly_chats_days = QLineEdit(self)
        self.readonly_chats_list = QListWidget(self)

        self.find_unread_chats_button = QPushButton(self)
        self.unread_chats_days = QLineEdit(self)
        self.unread_chats_list = QListWidget(self)

        self.find_inactive_users_button = QPushButton(self)
        self.inactive_users_days = QLineEdit(self)
        self.inactive_users_list = QListWidget(self)

        self.configure_elements()
        self.set_texts()

    @asyncSlot()
    async def leave_from_readonly_chats(self):
        chats = await self.get_readonly_chats()
        self.update_chats_widget(self.readonly_chats_list, chats)

    @asyncSlot()
    async def get_readonly_chats(self):
        await self.client.start()

        me = await self.client.get_me()
        groups_to_leave = []
        groups = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append(Group(dialog.id, dialog.title, dialog.name, dialog.is_channel,
                                    dialog.is_group, dialog.is_user, dialog.dialog.read_inbox_max_id,
                                    dialog.dialog.read_outbox_max_id,
                                    dialog.dialog.top_message, dialog.dialog.unread_count, dialog.archived,
                                    dialog.entity.date))

        for group in groups[:10]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity):
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.readonly_chats_days.text()))).timestamp():
                    groups_to_leave.append([group, str(message.date)])
                    break
                elif message.sender_id == me.id:
                    break

        return groups_to_leave

    @asyncSlot()
    async def leave_from_unread_chats(self):
        chats = await self.get_unread_chats()
        self.update_chats_widget(self.unread_chats_list, chats)

    @asyncSlot()
    async def get_unread_chats(self):
        await self.client.start()

        groups_to_leave = []
        groups = []

        async for dialog in self.client.iter_dialogs():
            if (dialog.is_group or dialog.is_channel) and dialog.dialog.unread_count > 0 \
                    and dialog.entity.megagroup is False and dialog.entity.gigagroup is False:
                groups.append(Group(dialog.id, dialog.title, dialog.name, dialog.is_channel,
                                    dialog.is_group, dialog.is_user, dialog.dialog.read_inbox_max_id,
                                    dialog.dialog.read_outbox_max_id,
                                    dialog.dialog.top_message, dialog.dialog.unread_count, dialog.archived,
                                    dialog.entity.date))

        for group in groups[:10]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity, offset_id=group.read_inbox_max_id):
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.unread_chats_days.text()))).timestamp():
                    groups_to_leave.append([group, str(message.date)])
                break

        return groups_to_leave

    @asyncSlot()
    async def kick_inactive_users(self):
        inactive_users = await self.get_inactive_users()
        users = []
        for group in inactive_users.keys():
            for user in inactive_users[group]:
                users.append([user, group])
        self.update_users_widget(self.inactive_users_list, users)

    @asyncSlot()
    async def get_inactive_users(self):
        await self.client.start()

        active_users = dict()
        inactive_users = dict()
        groups = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append(Group(dialog.id, dialog.title, dialog.name, dialog.is_channel,
                                    dialog.is_group, dialog.is_user, dialog.dialog.read_inbox_max_id,
                                    dialog.dialog.read_outbox_max_id,
                                    dialog.dialog.top_message, dialog.dialog.unread_count, dialog.archived,
                                    dialog.entity.date))

        for group in groups[:10]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity):
                if isinstance(message.sender, Channel):
                    continue
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.inactive_users_days.text()))).timestamp():
                    break
                if group not in active_users:
                    active_users[group] = {message.sender.id}
                else:
                    active_users[group].add(message.sender.id)

        for group in groups[:10]:
            all_users = await self.client.get_participants(group.id, aggressive=True)
            for user in all_users:
                if user.id not in active_users[group]:
                    if group not in inactive_users:
                        inactive_users[group] = [User(user.id, user.first_name, user.last_name, user.username)]
                    else:
                        inactive_users[group].append(User(user.id, user.first_name, user.last_name, user.username))

        return inactive_users

    @asyncClose
    async def closeEvent(self, event):
        pass

    def update_chats_widget(self, widget, chats):
        widget.clear()
        for chat in chats:
            list_adapter = DoubleListAdapter(name=locales[self.settings_window.locale]['title'],
                                             description=locales[self.settings_window.locale]['date'])
            list_adapter.set_name(chat[0].name)
            list_adapter.set_description(chat[1])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            widget.addItem(list_adapter_item)
            widget.setItemWidget(list_adapter_item, list_adapter)

    def update_users_widget(self, widget, users):
        widget.clear()
        for user in users:
            list_adapter = DoubleListAdapter(name=locales[self.settings_window.locale]['username'],
                                             description=locales[self.settings_window.locale]['title'])
            list_adapter.set_name(user[0].username)
            list_adapter.set_description(user[1].name)

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            widget.addItem(list_adapter_item)
            widget.setItemWidget(list_adapter_item, list_adapter)

    def set_texts(self):
        self.find_readonly_chats_button.setText(locales[self.settings_window.locale]['find_readonly_chats'])
        self.readonly_chats_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])

        self.find_unread_chats_button.setText(locales[self.settings_window.locale]['find_unread_chats'])
        self.unread_chats_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])

        self.find_inactive_users_button.setText(locales[self.settings_window.locale]['find_inactive_users'])
        self.inactive_users_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])

    def configure_elements(self) -> None:
        self.find_readonly_chats_button.clicked.connect(self.leave_from_readonly_chats)
        self.find_readonly_chats_button.setFixedHeight(BUTTON_HEIGHT)

        self.find_unread_chats_button.clicked.connect(self.leave_from_unread_chats)
        self.find_unread_chats_button.setFixedHeight(BUTTON_HEIGHT)

        self.find_inactive_users_button.clicked.connect(self.kick_inactive_users)
        self.find_inactive_users_button.setFixedHeight(BUTTON_HEIGHT)