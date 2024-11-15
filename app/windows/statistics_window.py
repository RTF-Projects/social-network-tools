import random
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout, QProgressBar, QVBoxLayout

from app.const import BUTTON_HEIGHT
from app.widgets.matplotlib_widget.matplotlib_widget import MatplotlibWidget


class StatisticsWindow(QWidget):
    def __init__(self):
        super().__init__()

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

        self.index_activity_widget_header = QWidget(self)
        self.index_activity_widget = QWidget(self)
        self.index_activity_chat_widget = MatplotlibWidget(500, 200)
        self.index_activity_hbox = QHBoxLayout()
        self.index_activity_vbox = QVBoxLayout()

        # Generate random participant data
        self.top_chat_names = ['УрФУ', 'ИРИТ-РТФ', 'Сбер', 'Python', 'Путешествия']
        self.top_chat_activity = [random.randint(35, 95) for _ in range(4)]
        self.top_chat_activity.append(100)
        self.all_chat_names = ['УрФУ', 'ИРИТ-РТФ', 'Сбер', 'Python', 'Путешествия', 'ФТИ', 'Проектный практикум']
        self.participants_all = random.randint(500, 1000)
        self.participants_today = random.randint(-10, -5)
        self.participants_week = random.randint(10, 50)
        self.participants_month = random.randint(60, 100)
        self.monthly_participant_statistics = [random.randint(-5, 15) for _ in range(30)]
        self.messages_all = random.randint(50000, 100000)
        self.messages_today = random.randint(25, 40)
        self.messages_week = random.randint(250, 500)
        self.messages_month = random.randint(600, 1000)
        self.monthly_message_statistics = [random.randint(25, 40) for _ in range(30)]
        self.mentions = random.randint(10, 30)
        self.reposts = random.randint(250, 350)
        self.rations = random.randint(200, 300)
        self.mentions_statistics = [random.randint(10, 30) for _ in range(24)]
        self.reposts_statistics = [random.randint(250, 350) for _ in range(24)]
        self.rations_statistics = [random.randint(200, 300) for _ in range(24)]

        self.configure_elements()
        self.set_texts()

    def update_chat_activity(self):
        chat_activity_label = QLabel(self)
        chat_activity_label.setText('Самые активные чаты')

        chat_activity_layout = QVBoxLayout(self)
        chat_activity_layout.addWidget(chat_activity_label)
        for i in range(len(self.top_chat_names)):
            chat_layout = QHBoxLayout()
            chat_label = QLabel(self.top_chat_names[i], self)
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
            chat_progress.setValue(self.top_chat_activity[i])
            chat_progress.setMaximum(100)

            chat_layout.addWidget(chat_label)
            chat_layout.addWidget(chat_progress)

            chat_widget = QWidget(self)
            chat_widget.setLayout(chat_layout)

            chat_activity_layout.addWidget(chat_widget)

        self.chat_activity_widget.setLayout(chat_activity_layout)

    def update_chat_selector(self):
        self.chat_selector.setFixedHeight(BUTTON_HEIGHT)

        for i, chat_name in enumerate(self.all_chat_names):
            self.chat_selector.addItem(chat_name)

    def update_participants(self):
        sign_today = '+' if self.participants_today >= 0 else '-'
        sign_week = '+' if self.participants_week >= 0 else '-'
        sign_month = '+' if self.participants_month >= 0 else '-'

        participants_label = QLabel(self)
        participants_all_label = QLabel(self)
        participants_today_label = QLabel(self)
        participants_week_label = QLabel(self)
        participants_month_label = QLabel(self)

        participants_label.setText('Участники')
        participants_all_label.setText(f'Всего: {self.participants_all}')
        participants_today_label.setText(f'За сегодня: {sign_today} {abs(self.participants_today)}')
        participants_week_label.setText(f'За неделю: {sign_week} {abs(self.participants_week)}')
        participants_month_label.setText(f'За месяц: {sign_month} {abs(self.participants_month)}')

        participants_vbox = QVBoxLayout(self.participants_widget)
        participants_vbox.addWidget(participants_label)
        participants_vbox.addWidget(participants_all_label)
        participants_vbox.addWidget(participants_today_label)
        participants_vbox.addWidget(participants_week_label)
        participants_vbox.addWidget(participants_month_label)

        self.participants_widget.setLayout(participants_vbox)

    def update_participants_chart(self):
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime('%d') for i in range(30)]

        self.participants_chat_widget.bar_graph(dates, self.monthly_participant_statistics, title='Статистика за месяц', x_label='День(число)')
        self.participants_chat_widget.setFixedWidth(500)
        self.participants_chat_widget.setFixedHeight(200)

    def update_messages(self):
        messages_label = QLabel(self)
        messages_all_label = QLabel(self)
        messages_today_label = QLabel(self)
        messages_week_label = QLabel(self)
        messages_month_label = QLabel(self)

        messages_label.setText('Сообщения')
        messages_all_label.setText(f'Всего: {self.messages_all}')
        messages_today_label.setText(f'За сегодня: {self.messages_today}')
        messages_week_label.setText(f'За неделю: {self.messages_week}')
        messages_month_label.setText(f'За месяц: {self.messages_month}')

        messages_vbox = QVBoxLayout(self.participants_widget)
        messages_vbox.addWidget(messages_label)
        messages_vbox.addWidget(messages_all_label)
        messages_vbox.addWidget(messages_today_label)
        messages_vbox.addWidget(messages_week_label)
        messages_vbox.addWidget(messages_month_label)

        self.messages_widget.setLayout(messages_vbox)

    def update_messages_chart(self):
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime('%d') for i in range(30)]

        self.messages_chat_widget.bar_graph(dates, self.monthly_message_statistics, title='Статистика за месяц', x_label='День(число)')
        self.messages_chat_widget.setFixedWidth(500)
        self.messages_chat_widget.setFixedHeight(200)

    def update_index_activity(self):
        index_activity_label = QLabel(self)
        period_of_times_selector = QComboBox(self)
        mentions_label = QLabel(self)
        reposts_label = QLabel(self)
        rations_label = QLabel(self)

        index_activity_label.setText('Индекс активности')
        index_activity_label.setFixedWidth(100)
        mentions_label.setText(f'Упоминаний: {self.mentions}')
        reposts_label.setText(f'Репостов: {self.reposts}')
        rations_label.setText(f'Реакций: {self.rations}')

        period_of_times = ['За сегодня', 'За месяц', 'За все время']
        for i, period_of_time in enumerate(period_of_times):
            period_of_times_selector.addItem(period_of_time)

        index_activity_hbox = QHBoxLayout(self)
        index_activity_hbox.addWidget(index_activity_label)
        index_activity_hbox.addWidget(period_of_times_selector)

        index_activity_vbox = QVBoxLayout(self)
        index_activity_vbox.addWidget(mentions_label)
        index_activity_vbox.addWidget(reposts_label)
        index_activity_vbox.addWidget(rations_label)

        self.index_activity_widget_header.setLayout(index_activity_hbox)
        self.index_activity_widget.setLayout(index_activity_vbox)

    def update_index_activity_chart(self):
        labels = ['Упоминания', 'Репосты', 'Реакции']
        data = [self.mentions_statistics, self.reposts_statistics, self.rations_statistics]

        today = datetime.now()
        dates = [(today - timedelta(hours=i)).strftime('%H:%M') for i in range(24)]

        self.index_activity_chat_widget.plot_graph(dates, data, labels, x_label='Время', title='Статистика за сутки')
        self.index_activity_chat_widget.setFixedWidth(1000)
        self.index_activity_chat_widget.setFixedHeight(300)

    def set_texts(self):
        pass

    def configure_elements(self):
        self.update_chat_activity()
        self.update_chat_selector()

        self.update_participants()
        self.update_participants_chart()
        self.participants_hbox.addWidget(self.participants_widget)
        self.participants_hbox.addWidget(self.participants_chat_widget)
        self.participants_combo_widget.setFixedWidth(600)
        self.participants_combo_widget.setLayout(self.participants_hbox)

        self.update_messages()
        self.update_messages_chart()
        self.messages_hbox.addWidget(self.messages_widget)
        self.messages_hbox.addWidget(self.messages_chat_widget)
        self.messages_combo_widget.setFixedWidth(600)
        self.messages_combo_widget.setLayout(self.messages_hbox)

        _messages_and_participants_widget = QHBoxLayout(self)
        _messages_and_participants_widget.addWidget(self.participants_combo_widget)
        _messages_and_participants_widget.addWidget(self.messages_combo_widget)
        self.messages_and_participants_widget.setLayout(_messages_and_participants_widget)

        self.update_index_activity()
        self.update_index_activity_chart()
        self.index_activity_hbox.addWidget(self.index_activity_widget)
        self.index_activity_hbox.addWidget(self.index_activity_chat_widget)
        _index_activity_widget = QWidget(self)
        _index_activity_widget.setLayout(self.index_activity_hbox)

        self.index_activity_vbox.addWidget(self.index_activity_widget_header)
        self.index_activity_vbox.addWidget(_index_activity_widget)

        self.index_activity_combo_widget.setFixedWidth(1100)
        self.index_activity_combo_widget.setLayout(self.index_activity_vbox)
