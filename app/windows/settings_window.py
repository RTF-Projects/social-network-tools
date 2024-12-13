import json
import os

from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QLineEdit, QLabel
from telethon import TelegramClient

from app.const import BUTTON_HEIGHT
from app.locales.locales import locales


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tab_widget = None
        self.telegram_window = None
        self.vk_window = None

        self.locale = ''
        self.locales = ['ru', 'en']

        self.system_version_telegram = "4.16.30-vxCUSTOM"
        self.session_name_telegram = "session_name"
        self.token_telegram = None
        self.token_hash_telegram = None

        self.token_input_label_telegram = QLabel(self)
        self.token_hash_input_label_telegram = QLabel(self)
        self.token_input_telegram = QLineEdit(self)
        self.token_hash_input_telegram = QLineEdit(self)
        self.locale_combobox = QComboBox(self)
        self.save_button = QPushButton(self)

        self.init_config_file()
        self.load_configuration()

        self.client = TelegramClient(self.session_name_telegram,
                                     self.token_telegram,
                                     self.token_hash_telegram,
                                     system_version=self.system_version_telegram)

        self.configure_elements()
        self.set_texts()

    def update_all_texts(self):
        self.locale = self.locales[self.locale_combobox.currentIndex()]
        self.set_texts()
        self.tab_widget.set_texts()
        self.telegram_window.set_texts()
        self.vk_window.set_texts()

    def set_texts(self):
        self.save_button.setText(locales[self.locale]['save'])

        self.token_input_label_telegram.setText(locales[self.locale]['token_telegram'])
        self.token_hash_input_label_telegram.setText(locales[self.locale]['token_hash_telegram'])

        self.locale_combobox.setItemText(0, locales[self.locale]['russian'])
        self.locale_combobox.setItemText(1, locales[self.locale]['english'])

    #TODO Telegram token int parsing
    def save(self):
        if self.token_input_telegram.text() == '':
            self.token_telegram = 0
        else:
            self.token_telegram = int(self.token_input_telegram.text())
        self.token_hash_telegram = self.token_hash_input_telegram.text()
        self.update_all_texts()
        self.save_config_file()

    def save_config_file(self):
        config_data = {
            "locale": self.locales[self.locale_combobox.currentIndex()],
            "token": self.token_input_telegram.text(),
            "token_hash": self.token_hash_input_telegram.text()
        }
        json_config_data = json.dumps(config_data, indent=4)
        with open('config.json', 'w') as f:
            f.write(json_config_data)

    # TODO Telegram token int parsing
    def load_configuration(self):
        with open('config.json', 'r') as f:
            config_data = json.loads(f.read())
            self.locale = config_data["locale"]
            if config_data["token"] == '':
                self.token_telegram = 0
            else:
                self.token_telegram = int(config_data["token"])
            self.token_hash_telegram = config_data["token_hash"]

    @staticmethod
    def init_config_file():
        config_data = {
            "locale": 'ru',
            "token": '',
            "token_hash": ''
        }
        json_config_data = json.dumps(config_data, indent=4)
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as f:
                f.write(json_config_data)

    def configure_elements(self) -> None:
        self.token_input_telegram.setText(str(self.token_telegram))
        self.token_hash_input_telegram.setText(self.token_hash_telegram)

        self.token_input_telegram.setEchoMode(QLineEdit.Password)
        self.token_hash_input_telegram.setEchoMode(QLineEdit.Password)

        self.save_button.clicked.connect(self.save)
        self.save_button.setFixedHeight(BUTTON_HEIGHT)

        self.locale_combobox.setFixedHeight(BUTTON_HEIGHT)
        self.locale_combobox.addItem('')
        self.locale_combobox.addItem('')
        self.locale_combobox.setCurrentIndex(self.locales.index(self.locale))
