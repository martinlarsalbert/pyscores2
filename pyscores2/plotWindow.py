import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import PyQt4.QtGui as QtGui
import numpy as np


class PlotWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent

        self.setGeometry(300, 300, 600, 800)

        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)

    def plot(self, x, y, xLabel, yLabel, title):

        self.setWindowTitle(title)

        x = np.array(x)
        y = np.array(y)

        self.axes = self.fig.add_subplot(111)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

        self.axes.clear()
        self.axes.grid(True)

        self.axes.plot(x, y)
        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)
        self.axes.set_title(title)

        self.show()

    def plot2(self, x1, y1, x2, y2, xLabel, yLabel, title):

        self.setWindowTitle(title)

        x1 = np.array(x1)
        y1 = np.array(y1)

        x2 = np.array(x2)
        y2 = np.array(y2)

        self.axes = self.fig.add_subplot(111)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

        self.axes.clear()
        self.axes.grid(True)

        p1 = self.axes.plot(x1, y1)
        p2 = self.axes.plot(x2, y2)

        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)
        self.axes.set_title(title)

        self.show()
