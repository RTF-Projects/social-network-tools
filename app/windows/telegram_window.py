import asyncio
from datetime import datetime, timedelta

import aiohttp
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidgetItem, QListWidget, QComboBox
from qasync import asyncSlot, asyncClose
from telethon import TelegramClient
from telethon.tl.types import Channel

from app.const import BUTTON_HEIGHT
from app.entities.group import Group
from app.entities.user import User
from app.locales.locales import locales
from app.widgets.layouts.line_3_layout import Line3Layout
from app.widgets.list_adapter_widget.single_list_adapter_widget import SingleListAdapter
from app.widgets.list_adapter_widget.double_list_adapter_widget import DoubleListAdapter


#TODO TG access confirmation window


class TelegramWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window

        self.client = self.settings_window.client

        self.readonly_chats = []
        self.readonly_chats_count = QLineEdit(self)
        self.readonly_chats_days = QLineEdit(self)
        self.readonly_chats_list = QListWidget(self)
        self.find_readonly_chats_button = QPushButton(self)
        self.leave_readonly_chat_button = QPushButton(self)
        self.leave_readonly_chats_button = QPushButton(self)
        self.readonly_chats_layout = Line3Layout(self.find_readonly_chats_button,
                                                 self.leave_readonly_chat_button,
                                                 self.leave_readonly_chats_button)

        self.unread_chats = []
        self.unread_chats_count = QLineEdit(self)
        self.unread_chats_days = QLineEdit(self)
        self.unread_chats_list = QListWidget(self)
        self.find_unread_chats_button = QPushButton(self)
        self.leave_unread_chat_button = QPushButton(self)
        self.leave_unread_chats_button = QPushButton(self)
        self.unread_chats_layout = Line3Layout(self.find_unread_chats_button,
                                               self.leave_unread_chat_button,
                                               self.leave_unread_chats_button)

        self.inactive_users_with_group = []
        self.inactive_users_count = QLineEdit(self)
        self.inactive_users_days = QLineEdit(self)
        self.user_groups_combobox = QComboBox(self)
        self.inactive_users_list = QListWidget(self)
        self.find_inactive_users_button = QPushButton(self)
        self.kick_inactive_user_button = QPushButton(self)
        self.kick_inactive_users_button = QPushButton(self)
        self.inactive_users_layout = Line3Layout(self.find_inactive_users_button,
                                                 self.kick_inactive_user_button,
                                                 self.kick_inactive_users_button)

        self.configure_elements()
        self.set_texts()

    @asyncSlot()
    async def find_readonly_chats(self):
        self.readonly_chats = await self.get_readonly_chats()
        self.update_readonly_chats_widget(self.readonly_chats_list, self.readonly_chats)

    @asyncSlot()
    async def leave_readonly_chat(self):
        await self.client.start()
        index = self.readonly_chats_list.currentRow()
        chat = self.readonly_chats[index]
        await self.client.kick_participant(chat[0].id, 'me')

    @asyncSlot()
    async def leave_readonly_chats(self):
        await self.client.start()
        chats = self.readonly_chats
        for chat in chats:
            await self.client.kick_participant(chat[0].id, 'me')

    @asyncSlot()
    async def get_readonly_chats(self):
        if self.readonly_chats_days.text() == '':
            return

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

        for group in groups[:(len(groups) if self.readonly_chats_count.text() == '' else int(self.readonly_chats_count.text()))]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity):
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.readonly_chats_days.text()))).timestamp():
                    groups_to_leave.append(group)
                    break
                elif message.sender_id == me.id:
                    break

        return groups_to_leave

    @asyncSlot()
    async def find_unread_chats(self):
        self.unread_chats = await self.get_unread_chats()
        self.update_unread_chats_widget(self.unread_chats_list, self.unread_chats)

    @asyncSlot()
    async def leave_unread_chat(self):
        await self.client.start()
        index = self.unread_chats_list.currentRow()
        chat = self.unread_chats[index]
        await self.client.kick_participant(chat[0].id, 'me')

    @asyncSlot()
    async def leave_unread_chats(self):
        await self.client.start()
        chats = self.unread_chats
        for chat in chats:
            await self.client.kick_participant(chat[0].id, 'me')

    @asyncSlot()
    async def get_unread_chats(self):
        if self.unread_chats_days.text() == '':
            return

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

        for group in groups[:(len(groups) if self.unread_chats_count.text() == '' else int(self.unread_chats_count.text()))]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity, offset_id=group.read_inbox_max_id):
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.unread_chats_days.text()))).timestamp():
                    groups_to_leave.append([group, str(message.date)])
                break

        return groups_to_leave

    @asyncSlot()
    async def find_inactive_users(self):
        self.user_groups_combobox.clear()
        self.inactive_users_with_group = []
        users = await self.get_inactive_users()
        for group in users.keys():
            self.user_groups_combobox.addItem(group.name)
            for user in users[group]:
                self.inactive_users_with_group.append([user, group])
        self.update_inactive_users_widget()

    @asyncSlot()
    async def kick_inactive_user(self):
        await self.client.start()
        index = self.inactive_users_list.currentRow()
        user_with_group = [user_with_group for user_with_group in self.inactive_users_with_group if
                           user_with_group[1].name == self.user_groups_combobox.currentText()][index]
        user = await self.client.get_entity(user_with_group[0].id)
        await self.client.kick_participant(user_with_group[1].id, user)

    @asyncSlot()
    async def kick_inactive_users(self):
        await self.client.start()
        users_with_group = [user_with_group for user_with_group in self.inactive_users_with_group if
                           user_with_group[1].name == self.user_groups_combobox.currentText()]
        for user_with_group in users_with_group:
            user = await self.client.get_entity(user_with_group[0].id)
            await self.client.kick_participant(user_with_group[1].id, user)

    @asyncSlot()
    async def get_inactive_users(self):
        if self.inactive_users_days.text() == '':
            return

        await self.client.start()

        active_users = dict()
        inactive_users = dict()
        groups = []

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group and dialog.entity.creator:
                groups.append(Group(dialog.id, dialog.title, dialog.name, dialog.is_channel,
                                    dialog.is_group, dialog.is_user, dialog.dialog.read_inbox_max_id,
                                    dialog.dialog.read_outbox_max_id,
                                    dialog.dialog.top_message, dialog.dialog.unread_count, dialog.archived,
                                    dialog.entity.date))

        for group in groups[:(len(groups) if self.inactive_users_count.text() == '' else int(self.inactive_users_count.text()))]:
            group_entity = await self.client.get_entity(group.id)
            async for message in self.client.iter_messages(group_entity):
                if isinstance(message.sender, Channel):
                    continue
                if message.date.timestamp() < (datetime.today() - timedelta(days=int(self.inactive_users_days.text()))).timestamp():
                    break
                try:
                    if group not in active_users:
                        active_users[group.id] = {message.sender.id}
                    else:
                        active_users[group.id].add(message.sender.id)
                except AttributeError:
                    continue

        for group in groups[:(len(groups) if self.inactive_users_count.text() == '' else int(self.inactive_users_count.text()))]:
            all_users = await self.client.get_participants(group.id, aggressive=True)
            for user in all_users:
                if active_users.get(group.id) is None or user.id not in active_users.get(group.id):
                    if group not in inactive_users:
                        inactive_users[group] = [User(user.id, user.first_name, user.last_name, user.username)]
                    else:
                        inactive_users[group].append(User(user.id, user.first_name, user.last_name, user.username))

        return inactive_users

    @asyncClose
    async def closeEvent(self, event):
        pass

    @staticmethod
    def update_readonly_chats_widget(widget, chats):
        widget.clear()
        for chat in chats:
            list_adapter = SingleListAdapter()
            list_adapter.set_first_column_title(chat.name)

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            widget.addItem(list_adapter_item)
            widget.setItemWidget(list_adapter_item, list_adapter)

    def update_unread_chats_widget(self, widget, chats_with_date):
        widget.clear()
        for chat_with_date in chats_with_date:
            list_adapter = DoubleListAdapter(first=locales[self.settings_window.locale]['title'],
                                             second=locales[self.settings_window.locale]['date'])
            list_adapter.set_first_column_title(chat_with_date[0].name)
            list_adapter.set_second_column_title(chat_with_date[1])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            widget.addItem(list_adapter_item)
            widget.setItemWidget(list_adapter_item, list_adapter)

    def update_inactive_users_widget(self):
        self.inactive_users_list.clear()
        for user_with_group in self.inactive_users_with_group:
            if self.user_groups_combobox.currentText() != '' and user_with_group[1].name != self.user_groups_combobox.currentText():
                continue

            list_adapter = DoubleListAdapter(first=locales[self.settings_window.locale]['username'],
                                             second=locales[self.settings_window.locale]['title'])
            list_adapter.set_first_column_title(user_with_group[0].username)
            list_adapter.set_second_column_title(user_with_group[1].name)

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.inactive_users_list.addItem(list_adapter_item)
            self.inactive_users_list.setItemWidget(list_adapter_item, list_adapter)

    def set_texts(self):
        self.find_readonly_chats_button.setText(locales[self.settings_window.locale]['find_readonly_chats'])
        self.leave_readonly_chat_button.setText(locales[self.settings_window.locale]['leave'])
        self.leave_readonly_chats_button.setText(locales[self.settings_window.locale]['leave_all'])
        self.readonly_chats_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])
        self.readonly_chats_count.setPlaceholderText(locales[self.settings_window.locale]['enter_max_entities_count'])

        self.find_unread_chats_button.setText(locales[self.settings_window.locale]['find_unread_chats'])
        self.leave_unread_chat_button.setText(locales[self.settings_window.locale]['leave'])
        self.leave_unread_chats_button.setText(locales[self.settings_window.locale]['leave_all'])
        self.unread_chats_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])
        self.unread_chats_count.setPlaceholderText(locales[self.settings_window.locale]['enter_max_entities_count'])

        self.find_inactive_users_button.setText(locales[self.settings_window.locale]['find_inactive_users'])
        self.kick_inactive_user_button.setText(locales[self.settings_window.locale]['kick'])
        self.kick_inactive_users_button.setText(locales[self.settings_window.locale]['kick_all'])
        self.inactive_users_days.setPlaceholderText(locales[self.settings_window.locale]['enter_days_number'])
        self.inactive_users_count.setPlaceholderText(locales[self.settings_window.locale]['enter_max_entities_count'])

    def configure_elements(self) -> None:
        int_validator = QIntValidator()
        int_validator.setRange(0, 9999)

        self.find_readonly_chats_button.clicked.connect(self.find_readonly_chats)
        self.leave_readonly_chat_button.clicked.connect(self.leave_readonly_chat)
        self.leave_readonly_chats_button.clicked.connect(self.leave_readonly_chats)
        self.find_readonly_chats_button.setFixedHeight(BUTTON_HEIGHT)
        self.leave_readonly_chat_button.setFixedHeight(BUTTON_HEIGHT)
        self.leave_readonly_chats_button.setFixedHeight(BUTTON_HEIGHT)
        self.readonly_chats_days.setValidator(int_validator)
        self.readonly_chats_count.setValidator(int_validator)

        self.find_unread_chats_button.clicked.connect(self.find_unread_chats)
        self.leave_unread_chat_button.clicked.connect(self.leave_unread_chat)
        self.leave_unread_chats_button.clicked.connect(self.leave_unread_chats)
        self.find_unread_chats_button.setFixedHeight(BUTTON_HEIGHT)
        self.leave_unread_chat_button.setFixedHeight(BUTTON_HEIGHT)
        self.leave_unread_chats_button.setFixedHeight(BUTTON_HEIGHT)
        self.unread_chats_days.setValidator(int_validator)
        self.unread_chats_count.setValidator(int_validator)

        self.find_inactive_users_button.clicked.connect(self.find_inactive_users)
        self.kick_inactive_user_button.clicked.connect(self.kick_inactive_user)
        self.kick_inactive_users_button.clicked.connect(self.kick_inactive_users)
        self.find_inactive_users_button.setFixedHeight(BUTTON_HEIGHT)
        self.kick_inactive_user_button.setFixedHeight(BUTTON_HEIGHT)
        self.kick_inactive_users_button.setFixedHeight(BUTTON_HEIGHT)
        self.inactive_users_days.setValidator(int_validator)
        self.inactive_users_count.setValidator(int_validator)
        self.user_groups_combobox.currentTextChanged.connect(self.update_inactive_users_widget)
