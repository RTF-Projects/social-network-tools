from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QGridLayout

from app.locales.locales import locales
from app.windows.telegram_window import TelegramWindow
from app.windows.vk_window import VKWindow
from app.windows.settings_window import SettingsWindow


class TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.telegram_tab = QWidget()
        self.vk_tab = QWidget()
        self.settings_tab = QWidget()
        self.setFixedSize(1600, 1200)

        self.settings_window = SettingsWindow()
        self.telegram_window = TelegramWindow(self.settings_window)
        self.vk_window = VKWindow(self.settings_window)

        self.settings_window.telegram_window = self.telegram_window
        self.settings_window.vk_window = self.vk_window
        self.settings_window.tab_widget = self

        self.tabs.addTab(self.telegram_tab, '')
        self.tabs.addTab(self.vk_tab, '')
        self.tabs.addTab(self.settings_tab, '')

        self.telegram_tab.layout = QGridLayout(self)
        self.telegram_tab.setLayout(self.telegram_tab.layout)

        self.vk_tab.layout = QVBoxLayout(self)
        self.vk_tab.setLayout(self.vk_tab.layout)

        self.settings_tab.layout = QVBoxLayout(self)
        self.settings_tab.layout.addWidget(self.settings_window.token_input_label_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_input_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_hash_input_label_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.token_hash_input_telegram)
        self.settings_tab.layout.addWidget(self.settings_window.locale_combobox)
        self.settings_tab.layout.addWidget(self.settings_window.save_button)
        self.settings_tab.layout.addStretch()
        self.settings_tab.setLayout(self.settings_tab.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.set_texts()
        self.show()

    def set_texts(self):
        self.tabs.setTabText(0, locales[self.settings_window.locale]['telegram'])
        self.tabs.setTabText(1, locales[self.settings_window.locale]['vk'])
        self.tabs.setTabText(2, locales[self.settings_window.locale]['settings'])
