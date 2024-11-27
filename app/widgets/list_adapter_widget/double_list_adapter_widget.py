from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout


class DoubleListAdapter(QWidget):
    def __init__(self, parent=None, first=None, second=None):
        super(DoubleListAdapter, self).__init__(parent)

        self.vBox = QVBoxLayout()
        self.first = QLabel()
        self.first_label = QLabel(first)
        self.first_label.setStyleSheet('QLabel { color: grey; }')
        self.vBox.addWidget(self.first_label)
        self.vBox.addWidget(self.first)

        self.vBoxSecond = QVBoxLayout()
        self.second = QLabel()
        self.second_label = QLabel(second)
        self.second_label.setStyleSheet('QLabel { color: grey; }')
        self.vBoxSecond.addWidget(self.second_label)
        self.vBoxSecond.addWidget(self.second)

        self.hBox = QHBoxLayout()
        self.hBox.addLayout(self.vBox)
        self.hBox.addLayout(self.vBoxSecond)
        self.setLayout(self.hBox)

    def set_first_column_title(self, text):
        self.first.setText(text)

    def set_second_column_title(self, text):
        self.second.setText(text)
