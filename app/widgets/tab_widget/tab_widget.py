from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from app.locales.locales import locales

# вкладки
from app.windows.telegram_window import TelegramWindow
from app.windows.vk_window import VKWindow
from app.windows.settings_window import SettingsWindow
from app.windows.statistics_window import StatisticsWindow


class TabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1600, 1200)

        # Главный layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Сам navbar
        self.nav_panel = QWidget(self)
        self.nav_panel.setStyleSheet("background-color: #34495E; padding: 10px;")
        self.nav_panel_layout = QHBoxLayout(self.nav_panel)
        self.nav_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки навигации для navbar
        self.telegram_button = QPushButton()
        self.vk_button = QPushButton()
        self.settings_button = QPushButton()
        self.statistics_button = QPushButton()

        # добавление кнопок в navbar
        for button in [self.telegram_button, self.vk_button, self.settings_button, self.statistics_button]:
            self._style_button(button)
            self.nav_panel_layout.addWidget(button)

        # содержимое с помощью QStackedWidget
        self.content = QStackedWidget(self)


        self.settings_window = SettingsWindow()
        self.telegram_window = TelegramWindow(self.settings_window)
        self.vk_window = VKWindow(self.settings_window)
        self.statistics_window = StatisticsWindow(self.settings_window)

        self.settings_window.telegram_window = self.telegram_window
        self.settings_window.vk_window = self.vk_window
        self.settings_window.tab_widget = self

        # создаем окна для вкладок
        self.telegram_tab = QWidget()
        self.vk_tab = QWidget()
        self.settings_tab = QWidget()
        self.statistics_tab = QWidget()

        # заполняем вкладки контентом
        self._fill_telegram_tab()
        self._fill_vk_tab()
        self._fill_settings_tab()
        self._fill_statistics_tab()

        # добавляем вкладки в QStackedWidget
        self.content.addWidget(self.telegram_tab)    # Вкладка 0
        self.content.addWidget(self.vk_tab)          # Вкладка 1
        self.content.addWidget(self.settings_tab)    # Вкладка 2
        self.content.addWidget(self.statistics_tab)  # Вкладка 3

        # добавляем navbar в главный layout
        self.layout.addWidget(self.nav_panel)
        self.layout.addWidget(self.content)
        self.setLayout(self.layout)

        # ставим начальный экран
        self.content.setCurrentIndex(0)
        self._set_active_button(self.telegram_button)

        # Устанавливаем тексты кнопок
        self.set_texts()
        self._add_icons()

        # подключение сигналов (переключение вкладок кнопками navbar-а)
        self.telegram_button.clicked.connect(lambda: self._switch_tab(0, self.telegram_button))
        self.vk_button.clicked.connect(lambda: self._switch_tab(1, self.vk_button))
        self.settings_button.clicked.connect(lambda: self._switch_tab(2, self.settings_button))
        self.statistics_button.clicked.connect(lambda: self._switch_tab(3, self.statistics_button))

    def set_texts(self):
        """ставим тексты кнопок навигационной панели"""
        locale = self.settings_window.locale  # Предполагается, что locale задается в SettingsWindow
        self.telegram_button.setText(locales[locale]['telegram'])
        self.vk_button.setText(locales[locale]['vk'])
        self.settings_button.setText(locales[locale]['settings'])
        self.statistics_button.setText(locales[locale]['statistics_telegram'])

    def _add_icons(self):
        """Добавляет иконки к кнопкам навигации"""
        self.telegram_button.setIcon(QIcon('./app/styles/tg_icon.svg'))
        self.vk_button.setIcon(QIcon('./app/styles/vk_icon.svg'))
        self.settings_button.setIcon(QIcon('./app/styles/setting_icon.png'))
        self.statistics_button.setIcon(QIcon('./app/styles/statistics_icon.svg'))
        for button in [self.telegram_button, self.vk_button, self.settings_button, self.statistics_button]:
            button.setIconSize(QSize(24, 24))  # Устанавливаем размер иконки

    def _switch_tab(self, index, button):
        """переключение вкладки и подсветка активной кнопки"""
        self.content.setCurrentIndex(index)
        self._set_active_button(button)

    def _fill_telegram_tab(self):
        """Содержимое вкладки Telegram-а"""
        self.telegram_tab.layout = QVBoxLayout(self)
        self.telegram_tab.layout.addWidget(self.telegram_window.readonly_chats_count)
        self.telegram_tab.layout.addWidget(self.telegram_window.readonly_chats_days)
        self.telegram_tab.layout.addWidget(self.telegram_window.readonly_chats_list)
        self.telegram_tab.layout.addWidget(self.telegram_window.readonly_chats_layout)

        self.telegram_tab.layout.addStretch()

        self.telegram_tab.layout.addWidget(self.telegram_window.unread_chats_count)
        self.telegram_tab.layout.addWidget(self.telegram_window.unread_chats_days)
        self.telegram_tab.layout.addWidget(self.telegram_window.unread_chats_list)
        self.telegram_tab.layout.addWidget(self.telegram_window.unread_chats_layout)

        self.telegram_tab.layout.addStretch()

        self.telegram_tab.layout.addWidget(self.telegram_window.inactive_users_count)
        self.telegram_tab.layout.addWidget(self.telegram_window.inactive_users_days)
        self.telegram_tab.layout.addWidget(self.telegram_window.user_groups_combobox)
        self.telegram_tab.layout.addWidget(self.telegram_window.inactive_users_list)
        self.telegram_tab.layout.addWidget(self.telegram_window.inactive_users_layout)

        self.telegram_tab.setLayout(self.telegram_tab.layout)

    def _fill_vk_tab(self):
        """Содержимое вкладки VK"""
        self.vk_tab.layout = QVBoxLayout(self)
        self.vk_tab.setLayout(self.vk_tab.layout)

    def _fill_settings_tab(self):
        """Содержимое вкладки настроек"""
        self.settings_tab.layout = QVBoxLayout(self)
        self.settings_tab.layout.addWidget(self.settings_window.token_input_label_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_input_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_hash_input_label_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_hash_input_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.locale_combobox)
        self.settings_tab.layout.addWidget(self.settings_window.save_button)
        self.settings_tab.layout.addStretch()
        self.settings_tab.setLayout(self.settings_tab.layout)

    def _fill_statistics_tab(self):
        """Содержимое вкладки статистики"""
        self.statistics_tab.layout = QVBoxLayout(self)
        self.statistics_tab.layout.addWidget(self.statistics_window.load_button)
        self.statistics_tab.layout.addWidget(self.statistics_window.chat_activity_widget)
        self.statistics_tab.layout.addWidget(self.statistics_window.chat_selector)
        self.statistics_tab.layout.addWidget(self.statistics_window.messages_and_participants_widget)
        self.statistics_tab.layout.addWidget(self.statistics_window.index_activity_combo_widget)
        self.statistics_tab.layout.addStretch()
        self.statistics_tab.setLayout(self.statistics_tab.layout)

    def _style_button(self, button):
        """Метод для стилизации кнопок на панели"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                width: 300px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        button.setFixedSize(200, 50)  # Увеличиваем ширину кнопок

    def _set_active_button(self, active_button):
        """Метод для подсветки активной кнопки"""
        buttons = [self.telegram_button, self.vk_button, self.settings_button, self.statistics_button]
        for button in buttons:
            if button == active_button:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #1F618D;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-size: 16px;
                        font-weight: bold;
                        text-align: center;
                    }
                """)
            else:
                self._style_button(button)
