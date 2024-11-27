from datetime import datetime, timedelta, timezone

from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QProgressBar, QVBoxLayout, QPushButton
from telethon import TelegramClient
from qasync import asyncSlot
from telethon.tl.types import MessageEntityMention, MessageActionChatAddUser, MessageActionChatJoinedByLink

from app.const import BUTTON_HEIGHT
from app.widgets.matplotlib_widget.matplotlib_widget import MatplotlibWidget


class StatisticsWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window
        self.client = TelegramClient(self.settings_window.session_name_telegram, self.settings_window.token_telegram, self.settings_window.token_hash_telegram, system_version=self.settings_window.system_version_telegram)

        self.chat_activity_widget = QWidget(self)
        self.chat_selector = QComboBox(self)
        self.messages_and_participants_widget = QWidget(self)
        self.index_activity_combo_widget = QWidget(self)
        self.participants_combo_widget = QWidget(self)
        self.participants_widget = QWidget(self)
        self.participants_chat_widget = MatplotlibWidget(500, 200)
        self.participants_hbox = QHBoxLayout()
        self.messages_combo_widget = QWidget(self)
        self.messages_widget = QWidget(self)
        self.messages_chat_widget = MatplotlibWidget(500, 200)
        self.messages_hbox = QHBoxLayout()
        self.index_activity_widget = QWidget(self)
        self.index_activity_chat_widget = MatplotlibWidget(500, 200)
        self.index_activity_hbox = QHBoxLayout()
        self.index_activity_vbox = QVBoxLayout()
        self.load_button = QPushButton(self)
        self.load_button_vbox = QVBoxLayout()
        self.load_button_vbox.addWidget(self.load_button)
        self.messages_label = QLabel(self)
        self.messages_today_label = QLabel(self)
        self.messages_week_label = QLabel(self)
        self.messages_month_label = QLabel(self)
        self.messages_vbox = QVBoxLayout(self.participants_widget)
        self.participants_label = QLabel(self)
        self.participants_all_label = QLabel(self)
        self.participants_today_label = QLabel(self)
        self.participants_week_label = QLabel(self)
        self.participants_month_label = QLabel(self)
        self.participants_vbox = QVBoxLayout(self.participants_widget)
        self.index_activity_label = QLabel(self)
        self.mentions_label = QLabel(self)
        self.mentions_label_today = QLabel(self)
        self.mentions_label_week = QLabel(self)
        self.mentions_label_month = QLabel(self)
        self.reposts_label = QLabel(self)
        self.reposts_label_today = QLabel(self)
        self.reposts_label_week = QLabel(self)
        self.reposts_label_month = QLabel(self)
        self.rations_label = QLabel(self)
        self.rations_label_today = QLabel(self)
        self.rations_label_week = QLabel(self)
        self.rations_label_month = QLabel(self)
        self.index_activity_vbox_copy = QVBoxLayout(self)

        self.active_chats = []
        self.all_chats = []
        self.chat_statistics = {}
        self.participants_statistics = {}
        self.index_activity = {}

        self.configure_elements()
        self.set_texts()


    @asyncSlot()
    async def load_data(self):
        self.load_button.setEnabled(False)
        self.chat_selector.blockSignals(True)
        self.chat_selector.setEnabled(False)

        self.active_chats, self.all_chats = await self.get_active_chats()
        self.update_chat_activity()
        self.update_chat_selector()

        message_statistics = await self.get_messages_statistics(self.all_chats[0]['dialog_id'])

        self.chat_statistics = message_statistics['chat_statistics']
        self.update_messages()
        self.update_messages_chart()

        self.participants_statistics = message_statistics['participant_statistics']
        self.update_participants()
        self.update_participants_chart()

        self.index_activity = message_statistics['index_activity']
        self.update_index_activity()
        self.update_index_activity_chart()

        self.load_button.setEnabled(True)
        self.chat_selector.setEnabled(True)
        self.chat_selector.blockSignals(False)


    @asyncSlot()
    async def on_chat_selected(self):
        current_index = self.chat_selector.currentIndex()

        self.chat_selector.blockSignals(True)
        self.chat_selector.setEnabled(False)

        message_statistics = await self.get_messages_statistics(self.all_chats[current_index]['dialog_id'])

        self.chat_statistics = message_statistics['chat_statistics']
        self.update_messages()
        self.update_messages_chart()

        self.participants_statistics = message_statistics['participant_statistics']
        self.update_participants()
        self.update_participants_chart()

        self.index_activity = message_statistics['index_activity']
        self.update_index_activity()
        self.update_index_activity_chart()

        self.chat_selector.setEnabled(True)
        self.chat_selector.blockSignals(False)


    async def get_active_chats(self, days=7):
        await self.client.start()

        chats = []
        all_chats = []

        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                all_chats.append({'dialog_id': dialog.id, 'title': dialog.title})

            if dialog.is_group:
                group_entity = await self.client.get_entity(dialog.id)

                message_count = 0
                async for message in self.client.iter_messages(group_entity, offset_date=start_date, reverse=True):
                    if message.date >= start_date:
                        message_count += 1
                    else:
                        break

                print('title: ', dialog.title)
                print('message count: ', message_count)

                chats.append({'dialog_id': dialog.id, 'title': dialog.title, 'message_count': message_count})

        sorted_groups = sorted(chats, key=lambda x: x['message_count'], reverse=True)

        return sorted_groups, all_chats


    async def get_messages_statistics(self, dialog_id):
        await self.client.start()

        group_entity = await self.client.get_entity(dialog_id)

        now = datetime.now(timezone.utc)
        start_date_today = now - timedelta(days=1)
        start_date_week = now - timedelta(days=7)
        start_date_month = now - timedelta(days=30)

        chat_statistics_count_today = 0
        chat_statistics_count_week = 0
        chat_statistics_count_month = 0
        chat_statistics_daily_message_counts = {}

        total_count_participants = (await self.client.get_participants(dialog_id, limit=0)).total
        joined_today = 0
        joined_week = 0
        joined_month = 0
        daily_joins_counts = {}

        reposts_today = 0
        reposts_week = 0
        reposts_month = 0
        mentions_today = 0
        mentions_week = 0
        mentions_month = 0
        reactions_today = 0
        reactions_week = 0
        reactions_month = 0
        daily_reposts_counts = {}
        daily_mentions_counts = {}
        daily_reactions_counts = {}

        async for message in self.client.iter_messages(group_entity, offset_date=start_date_month, reverse=True):
            message_date = str(message.date.date())

            if message_date in chat_statistics_daily_message_counts:
                chat_statistics_daily_message_counts[message_date] += 1
            else:
                chat_statistics_daily_message_counts[message_date] = 1

            if message.date >= start_date_today:
                chat_statistics_count_today += 1
            if message.date >= start_date_week:
                chat_statistics_count_week += 1

            chat_statistics_count_month += 1

            if isinstance(message.action, (MessageActionChatAddUser, MessageActionChatJoinedByLink)):
                if message.date >= start_date_today:
                    joined_today += 1

                if message.date >= start_date_week:
                    joined_week += 1

                if message.date >= start_date_month:
                    joined_month += 1

                    if message_date in daily_joins_counts:
                        daily_joins_counts[message_date] += 1
                    else:
                        daily_joins_counts[message_date] = 1

            if message.fwd_from:
                if message.date >= start_date_today:
                    reposts_today += 1
                if message.date >= start_date_week:
                    reposts_week += 1
                if message.date >= start_date_month:
                    reposts_month += 1

                    if message_date in daily_reposts_counts:
                        daily_reposts_counts[message_date] += 1
                    else:
                        daily_reposts_counts[message_date] = 1

            if message.entities:
                for entity in message.entities:
                    if isinstance(entity, MessageEntityMention):
                        if message.date >= start_date_today:
                            mentions_today += 1
                        if message.date >= start_date_week:
                            mentions_week += 1
                        if message.date >= start_date_month:
                            mentions_month += 1

                            if message_date in daily_mentions_counts:
                                daily_mentions_counts[message_date] += 1
                            else:
                                daily_mentions_counts[message_date] = 1

            if message.reactions:
                reaction_count = sum(reaction.count for reaction in message.reactions.results)
                if message.date >= start_date_today:
                    reactions_today += reaction_count
                if message.date >= start_date_week:
                    reactions_week += reaction_count
                if message.date >= start_date_month:
                    reactions_month += reaction_count

                    if message_date in daily_reactions_counts:
                        daily_reactions_counts[message_date] += 1
                    else:
                        daily_reactions_counts[message_date] = 1

        daily_joins = {}
        chat_statistics_daily_counts = {}
        daily_reposts = {}
        daily_mentions = {}
        daily_reactions = {}

        for day_offset in range(30):
            day = now - timedelta(days=day_offset)
            day_str = str(day.date())

            if day_str in chat_statistics_daily_message_counts:
                chat_statistics_daily_counts[day_str] = chat_statistics_daily_message_counts[day_str]
            else:
                chat_statistics_daily_counts[day_str] = 0

            if day_str in daily_joins_counts:
                daily_joins[day_str] = daily_joins_counts[day_str]
            else:
                daily_joins[day_str] = 0

            if day_str in daily_reposts_counts:
                daily_reposts[day_str] = daily_reposts_counts[day_str]
            else:
                daily_reposts[day_str] = 0

            if day_str in daily_mentions_counts:
                daily_mentions[day_str] = daily_mentions_counts[day_str]
            else:
                daily_mentions[day_str] = 0

            if day_str in daily_reactions_counts:
                daily_reactions[day_str] = daily_reactions_counts[day_str]
            else:
                daily_reactions[day_str] = 0

        return {
            'chat_statistics': {
                'dialog_id': dialog_id,
                'count_today': chat_statistics_count_today,
                'count_week': chat_statistics_count_week,
                'count_month': chat_statistics_count_month,
                'daily_counts': chat_statistics_daily_counts
            },
            'participant_statistics':{
                'dialog_id': dialog_id,
                'total_count_participants': total_count_participants,
                'joined_today': joined_today,
                'joined_week': joined_week,
                'joined_month': joined_month,
                'daily_joins': daily_joins
            },
            'index_activity': {
                'reposts': {
                    'today': reposts_today,
                    'week': reposts_week,
                    'month': reposts_month,
                    'daily': daily_reposts,
                },
                'mentions': {
                    'today': mentions_today,
                    'week': mentions_week,
                    'month': mentions_month,
                    'daily': daily_mentions,
                },
                'reactions': {
                    'today': reactions_today,
                    'week': reactions_week,
                    'month': reactions_month,
                    'daily': daily_reactions,
                }
            }
        }


    def update_chat_activity(self):
        top_chats = self.active_chats[:5]

        top_chat_names = [chat['title'] for chat in top_chats]
        top_chat_activity = [chat['message_count'] for chat in top_chats]

        chat_activity_label = QLabel(self)
        chat_activity_label.setText('Самые активные чаты')

        chat_activity_layout = QVBoxLayout(self)
        chat_activity_layout.addWidget(chat_activity_label)
        max_value = max(top_chat_activity)

        for i, chat_name in enumerate(top_chat_names):
            chat_layout = QHBoxLayout()

            chat_label = QLabel(chat_name, self)
            chat_label.setFixedWidth(70)

            chat_progress = QProgressBar(self)
            chat_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                }
                QProgressBar::chunk {
                    background-color: green;
                    width: 100%;
                }
            """)

            chat_progress.setValue(int((top_chat_activity[i] / max_value) * 100))
            chat_progress.setMaximum(100)

            chat_layout.addWidget(chat_label)
            chat_layout.addWidget(chat_progress)

            chat_widget = QWidget(self)
            chat_widget.setLayout(chat_layout)
            chat_activity_layout.addWidget(chat_widget)

        self.chat_activity_widget.setLayout(chat_activity_layout)


    def update_chat_selector(self):
        self.chat_selector.blockSignals(True)
        self.chat_selector.clear()

        for i, chat in enumerate(self.all_chats):
            self.chat_selector.addItem(chat['title'])

        self.chat_selector.blockSignals(False)


    def update_messages(self):
        self.messages_label.setText('Сообщения')
        self.messages_today_label.setText(f'За 24 часа: {self.chat_statistics['count_today']}')
        self.messages_week_label.setText(f'За неделю: {self.chat_statistics['count_week']}')
        self.messages_month_label.setText(f'За месяц: {self.chat_statistics['count_month']}')


    def update_messages_chart(self):
        dates = list(self.chat_statistics['daily_counts'].keys())
        values = list(self.chat_statistics['daily_counts'].values())

        self.messages_chat_widget.bar_graph(dates, values, title='Статистика за месяц', x_label='День(число)')
        self.messages_chat_widget.setFixedWidth(500)
        self.messages_chat_widget.setFixedHeight(200)


    def update_participants(self):
        sign_today = '+' if self.participants_statistics['joined_today'] >= 0 else '-'
        sign_week = '+' if self.participants_statistics['joined_week'] >= 0 else '-'
        sign_month = '+' if self.participants_statistics['joined_month'] >= 0 else '-'

        self.participants_label.setText('Участники')
        self.participants_all_label.setText(f'Всего: {self.participants_statistics['total_count_participants']}')
        self.participants_today_label.setText(f'За 24 часа: {sign_today} {abs(self.participants_statistics['joined_today'])}')
        self.participants_week_label.setText(f'За неделю: {sign_week} {abs(self.participants_statistics['joined_week'])}')
        self.participants_month_label.setText(f'За месяц: {sign_month} {abs(self.participants_statistics['joined_month'])}')


    def update_participants_chart(self):
        dates = list(self.participants_statistics['daily_joins'].keys())
        values = list(self.participants_statistics['daily_joins'].values())

        self.participants_chat_widget.bar_graph(dates, values, title='Статистика за месяц', x_label='День(число)')
        self.participants_chat_widget.setFixedWidth(500)
        self.participants_chat_widget.setFixedHeight(200)


    def update_index_activity(self):
        self.index_activity_label.setText('Индекс активности')
        self.index_activity_label.setFixedWidth(100)

        self.mentions_label.setText(f'Упоминаний:')
        self.mentions_label_today.setText(f'За 24 часа: {self.index_activity['mentions']['today']}')
        self.mentions_label_week.setText(f'За неделю: {self.index_activity['mentions']['week']}')
        self.mentions_label_month.setText(f'За месяц: {self.index_activity['mentions']['month']}')

        self.reposts_label.setText(f'Репостов:')
        self.reposts_label_today.setText(f'За 24 часа: {self.index_activity['reposts']['today']}')
        self.reposts_label_week.setText(f'За неделю: {self.index_activity['reposts']['week']}')
        self.reposts_label_month.setText(f'За месяц: {self.index_activity['reposts']['month']}')

        self.rations_label.setText(f'Реакций:')
        self.rations_label_today.setText(f'За 24 часа: {self.index_activity['reactions']['today']}')
        self.rations_label_week.setText(f'За неделю: {self.index_activity['reactions']['week']}')
        self.rations_label_month.setText(f'За месяц: {self.index_activity['reactions']['month']}')


    def update_index_activity_chart(self):
        labels = ['Упоминания', 'Репосты', 'Реакции']

        dates = list(self.index_activity['mentions']['daily'].keys())
        values_mentions = list(self.index_activity['mentions']['daily'].values())
        values_reposts = list(self.index_activity['reposts']['daily'].values())
        values_reactions = list(self.index_activity['reactions']['daily'].values())

        data = [values_mentions, values_reposts, values_reactions]

        self.index_activity_chat_widget.axes.clear()
        self.index_activity_chat_widget.plot_graph(dates, data, labels, x_label='День(число)', title='Статистика за месяц')
        self.index_activity_chat_widget.setFixedWidth(1000)
        self.index_activity_chat_widget.setFixedHeight(300)


    def set_texts(self):
        self.load_button.setText('Загрузить статистику')


    def configure_elements(self):
        self.load_button.clicked.connect(self.load_data)
        self.chat_selector.currentTextChanged.connect(self.on_chat_selected)

        self.chat_selector.setFixedHeight(BUTTON_HEIGHT)

        self.participants_hbox.addWidget(self.participants_widget)
        self.participants_hbox.addWidget(self.participants_chat_widget)
        self.participants_combo_widget.setFixedWidth(600)
        self.participants_combo_widget.setLayout(self.participants_hbox)

        self.messages_hbox.addWidget(self.messages_widget)
        self.messages_hbox.addWidget(self.messages_chat_widget)
        self.messages_combo_widget.setFixedWidth(600)
        self.messages_combo_widget.setLayout(self.messages_hbox)

        _messages_and_participants_widget = QHBoxLayout(self)
        _messages_and_participants_widget.addWidget(self.participants_combo_widget)
        _messages_and_participants_widget.addWidget(self.messages_combo_widget)
        self.messages_and_participants_widget.setLayout(_messages_and_participants_widget)

        statistics_vbox = QVBoxLayout(self)
        statistics_vbox.addWidget(self.chat_activity_widget)
        statistics_vbox.addWidget(self.chat_selector)
        statistics_vbox.addWidget(self.messages_and_participants_widget)
        statistics_vbox.addWidget(self.index_activity_combo_widget)

        self.messages_vbox.addWidget(self.messages_label)
        self.messages_vbox.addWidget(self.messages_today_label)
        self.messages_vbox.addWidget(self.messages_week_label)
        self.messages_vbox.addWidget(self.messages_month_label)
        self.messages_widget.setLayout(self.messages_vbox)

        self.participants_vbox.addWidget(self.participants_label)
        self.participants_vbox.addWidget(self.participants_all_label)
        self.participants_vbox.addWidget(self.participants_today_label)
        self.participants_vbox.addWidget(self.participants_week_label)
        self.participants_vbox.addWidget(self.participants_month_label)
        self.participants_widget.setLayout(self.participants_vbox)

        self.mentions_label_today.setStyleSheet("padding-left: 20px;")
        self.mentions_label_week.setStyleSheet("padding-left: 20px;")
        self.mentions_label_month.setStyleSheet("padding-left: 20px;")
        self.reposts_label_today.setStyleSheet("padding-left: 20px;")
        self.reposts_label_week.setStyleSheet("padding-left: 20px;")
        self.reposts_label_month.setStyleSheet("padding-left: 20px;")
        self.rations_label_today.setStyleSheet("padding-left: 20px;")
        self.rations_label_week.setStyleSheet("padding-left: 20px;")
        self.rations_label_month.setStyleSheet("padding-left: 20px;")

        self.index_activity_vbox_copy.addWidget(self.mentions_label)
        self.index_activity_vbox_copy.addWidget(self.mentions_label_today)
        self.index_activity_vbox_copy.addWidget(self.mentions_label_week)
        self.index_activity_vbox_copy.addWidget(self.mentions_label_month)
        self.index_activity_vbox_copy.addWidget(self.reposts_label)
        self.index_activity_vbox_copy.addWidget(self.reposts_label_today)
        self.index_activity_vbox_copy.addWidget(self.reposts_label_week)
        self.index_activity_vbox_copy.addWidget(self.reposts_label_month)
        self.index_activity_vbox_copy.addWidget(self.rations_label)
        self.index_activity_vbox_copy.addWidget(self.rations_label_today)
        self.index_activity_vbox_copy.addWidget(self.rations_label_week)
        self.index_activity_vbox_copy.addWidget(self.rations_label_month)
        self.index_activity_widget.setLayout(self.index_activity_vbox_copy)

        self.index_activity_hbox.addWidget(self.index_activity_widget)
        self.index_activity_hbox.addWidget(self.index_activity_chat_widget)
        _index_activity_widget = QWidget(self)
        _index_activity_widget.setLayout(self.index_activity_hbox)
        self.index_activity_vbox.addWidget(self.index_activity_label)
        self.index_activity_vbox.addWidget(_index_activity_widget)
        self.index_activity_combo_widget.setFixedWidth(1100)
        self.index_activity_combo_widget.setLayout(self.index_activity_vbox)
