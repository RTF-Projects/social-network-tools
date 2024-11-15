from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MatplotlibWidget(FigureCanvasQTAgg):
    """Class for displaying matplotlib plot inside PyQt5"""

    def __init__(self, width = 10, height = 6):
        self.figure = Figure(figsize=(width, height))
        self.axes = self.figure.add_subplot(111)
        super(MatplotlibWidget, self).__init__(self.figure)

    def bar_graph(self, x, y, x_label='', y_label='', title=''):
        colors = ['blue' if value >= 0 else 'red' for value in y]

        self.axes.clear()
        self.axes.bar(x, y, color=colors)
        self.axes.axhline(0, color='black', linewidth=0.8)
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)
        self.axes.set_xticks(range(len(x)))
        self.axes.set_xticklabels(x, rotation=90)
        self.figure.subplots_adjust(bottom=0.25, left=0.08)
        self.draw()

    def plot_graph(self, x, y, y_label, x_label='',  title=''):
        if isinstance(y, list) and isinstance(y[0], list):
            for i, line in enumerate(y):
                color = ['blue', 'green', 'red'][i % 3]
                label = f'{y_label[i]}'
                self.axes.plot(x, line, color=color, label=label)
        else:
            self.axes.plot(x, y, color='blue', label=y_label)

        self.axes.axhline(0, color='black', linewidth=0.8)
        self.axes.set_xlabel(x_label)
        self.axes.set_title(title)
        self.axes.set_xticks(range(len(x)))
        self.axes.set_xticklabels(x, rotation=90)
        self.axes.legend()
        self.figure.subplots_adjust(bottom=0.18, left=0.08)
        self.draw()
