from PyQt5.QtWidgets import QGridLayout, QWidget


class Line3Layout(QWidget):
    def __init__(self, element_0_0, element_0_1, element_0_2):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(element_0_0, 0, 0)
        layout.addWidget(element_0_1, 0, 1)
        layout.addWidget(element_0_2, 0, 2)
