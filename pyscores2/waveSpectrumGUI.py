from PyQt4.QtCore import *
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from . import indata
import os.path
from . import output
import numpy as np
from . import plotWindow
import scipy.io
from . import waveSpectrum
import copy
import pickle
import datetime


class waveSpectrumWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(waveSpectrumWidget, self).__init__(parent)

        self.parent = parent
        self.waveSpectrums = []
        self.spectrumItemDict = {}  #Dictionary [QtspectrumItem] = spectrum no
        self.resultVariableDict = {}
        self.resultsVariableDict = {}

        self.scoresFile = None

        self.setWindowTitle('Spectrums')

        self.treeWidget = QtGui.QTreeWidget()
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 100, 200))
        self.treeWidget.setHeaderLabels([' ', 'Value'])
        self.setWidget(self.treeWidget)

        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treeWidget.customContextMenuRequested.connect(self.treePopup)

        self.actionAddSpectrum = QtGui.QAction(QtGui.QIcon('plus.png'),
                                               "Add Spectrum", self)
        self.actionAddSpectrum.triggered.connect(self.addSpectrumGUI)

        self.popMenu1 = QtGui.QMenu(self)
        self.popMenu1.addAction(self.actionAddSpectrum)

        self.actionEditSpectrum = QtGui.QAction("Edit", self)
        self.actionEditSpectrum.triggered.connect(self.editSpectrum)
        self.actionDeleteSpectrum = QtGui.QAction(QtGui.QIcon('exit.png'),
                                                  "Delete Spectrum", self)
        self.actionDeleteSpectrum.triggered.connect(self.deleteSpectrum)
        self.actionPlotSpectrum = QtGui.QAction("Plot", self)
        self.actionPlotSpectrum.triggered.connect(self.plotSpectrum)
        self.actionCalculate = QtGui.QAction("Calculate", self)
        self.actionCalculate.triggered.connect(self.calculate)

        self.popMenuSpectrum = QtGui.QMenu(self)
        self.popMenuSpectrum.addAction(self.actionEditSpectrum)
        self.popMenuSpectrum.addAction(self.actionPlotSpectrum)
        self.popMenuSpectrum.addAction(self.actionCalculate)
        self.popMenuSpectrum.addAction(self.actionDeleteSpectrum)

        self.actionShowIntegration = QtGui.QAction("Show integration", self)
        self.actionShowIntegration.triggered.connect(self.showIntegration)
        self.popMenuResult = QtGui.QMenu(self)
        self.popMenuResult.addAction(self.actionShowIntegration)

        self.actionCopyResults = QtGui.QAction("Copy", self)
        self.actionCopyResults.triggered.connect(self.copyResults)
        self.popMenuResults = QtGui.QMenu(self)
        self.popMenuResults.addAction(self.actionCopyResults)

        self.getEmptyTree()

    def getEmptyTree(self):
        parent = self.treeWidget.invisibleRootItem()
        column = 0
        title = "Spectrums"

        self.spectrumsItem = self.addParent(parent, column, title, title)

    def addParent(self, parent, column, title, data):
        item = QtGui.QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setExpanded(False)
        return item

    def treePopup(self, point):

        if self.treeWidget.currentItem() == self.spectrumsItem:
            self.popMenu1.exec_(self.treeWidget.mapToGlobal(point))
        elif self.treeWidget.currentItem() in self.spectrumItemDict:
            self.popMenuSpectrum.exec_(self.treeWidget.mapToGlobal(point))
        elif self.treeWidget.currentItem() in self.resultVariableDict:
            self.popMenuResult.exec_(self.treeWidget.mapToGlobal(point))
        elif self.treeWidget.currentItem() in self.resultsVariableDict:
            self.popMenuResults.exec_(self.treeWidget.mapToGlobal(point))

    def addSpectrumGUI(self, point):
        self.addSpectrum()

    def addSpectrum(self, newSpectrum=None):
        if newSpectrum == None:
            addSpectrumWindow = AddSpectrumWindow(self)
            addSpectrumWindow.exec_()

            if hasattr(addSpectrumWindow, 'waveSpectrum'):
                newSpectrum = addSpectrumWindow.waveSpectrum
            else:
                return

        self.waveSpectrums.append(newSpectrum)

        #Update the spectrum flag (for ScoresII only):
        spectrumType = newSpectrum.getType()
        if spectrumType == 'ITTCSpectrum':
            self.parent.scores2Indata.runOptions["ID"].set_value(
                3)  # Note that this equals a Two parameter spectrum.
        elif spectrumType == 'JonswapSpectrum':
            self.parent.scores2Indata.runOptions["ID"].set_value(6)
        #elif spectrumType == 'FileSpectrum':
        else:
            self.parent.scores2Indata.runOptions["ID"].set_value(0)

        spectrumItem = self.addParent(self.spectrumsItem, 0, newSpectrum.name,
                                      None)

        self.updateSpectrumWidget(spectrumItem, newSpectrum)

    def updateSpectrumWidget(self, spectrumItem, newSpectrum):

        self.spectrumsItem.setExpanded(True)
        spectrumItem.setExpanded(True)

        self.spectrumItemDict[spectrumItem] = len(self.waveSpectrums) - 1

        spectrumItem.takeChildren()
        parametersItem = self.addParent(spectrumItem, 0, "Parameters", None)
        parametersItem.setExpanded(True)

        parameterDictionary = newSpectrum.getParameterDict()
        for parameter in parameterDictionary.keys():
            parameterItem = QtGui.QTreeWidgetItem(
                parametersItem,
                [parameter, str(parameterDictionary[parameter])])
            parameterItem.setExpanded(True)

        self.treeWidget.resizeColumnToContents(0)

    def deleteSpectrum(self, point):

        currentSpectrumIndex = self.spectrumItemDict[
            self.treeWidget.currentItem()]

        self.treeWidget.currentItem().parent().removeChild(
            self.treeWidget.currentItem())

        self.waveSpectrums.pop(currentSpectrumIndex)

    def editSpectrum(self, point):

        currentSpectrumIndex = self.spectrumItemDict[
            self.treeWidget.currentItem()]
        spectrum = self.waveSpectrums[currentSpectrumIndex]

        addSpectrumWindow = AddSpectrumWindow(self, spectrum)
        addSpectrumWindow.exec_()

        self.waveSpectrums[
            currentSpectrumIndex] = addSpectrumWindow.waveSpectrum

        self.updateSpectrumWidget(self.treeWidget.currentItem(),
                                  addSpectrumWindow.waveSpectrum)

    def plotSpectrum(self):

        currentSpectrumIndex = self.spectrumItemDict[
            self.treeWidget.currentItem()]
        spectrum = self.waveSpectrums[currentSpectrumIndex]

        thePlotWindow = plotWindow.PlotWindow(self)

        yLabel = "Spectrum [m2*sec]"
        xLabel = "wave frequency [rad/s]"
        title = spectrum.getTitle()

        S = spectrum.get()
        frequencys = spectrum.frequencies

        thePlotWindow.plot(frequencys, S, xLabel, yLabel, title)

    def showIntegration(self):
        #This function plots the correponding wave spectrum and RAO togehter:

        resultIndex = self.resultVariableDict[self.treeWidget.currentItem()]
        speed = resultIndex["speed"]
        waveDirection = resultIndex["waveDirection"]
        kind = resultIndex["kind"]
        variable = resultIndex["variable"]

        currentSpectrumItem = self.treeWidget.currentItem().parent().parent(
        ).parent().parent().parent()
        currentSpectrumIndex = self.spectrumItemDict[currentSpectrumItem]
        spectrum = self.waveSpectrums[currentSpectrumIndex]
        result = spectrum.results[speed][waveDirection][kind][variable]

        thePlotWindow1 = plotWindow.PlotWindow(self)
        yLabel = "Spectrum [m2*sec]"
        xLabel = "wave frequency [rad/s]"
        title = "%s speed:%2.2f wave direction:%2.0f %s %s" % (
            spectrum.getTitle(), speed, waveDirection, kind, variable)

        thePlotWindow1.plot2(spectrum.frequencies, spectrum.S,
                             result.RAOFrequencies, result.RAO, xLabel, yLabel,
                             title)

    def calculate(self):
        #Calculate responses in the given wave spectra
        currentSpectrumIndex = self.spectrumItemDict[
            self.treeWidget.currentItem()]
        spectrum = self.waveSpectrums[currentSpectrumIndex]

        if self.scoresFile != None:
            spectrum.calculateFromScoresFile(self.scoresFile)
            self.addResult(self.treeWidget.currentItem(), spectrum)
        else:
            QtGui.QMessageBox.about(
                self, "Calculation error",
                "You have to get RAOs first. For instance by running ScoresII")

    def addResult(self, spectrumWidget, spectrum, resultName="Results"):
        #This function adds the result of an irregular sea calculation to the spectrum tree Widget.

        currentTime = datetime.datetime.now().time()
        resultName = resultName + " " + currentTime.isoformat()

        resultsItem = self.addParent(spectrumWidget, 0, resultName, None)
        resultsItem.setExpanded(True)

        self.resultsVariableDict[resultsItem] = spectrum

        for speed in sorted(spectrum.results.keys()):
            speedsItem = self.addParent(resultsItem, 0, "Speed: %4.2f" % speed,
                                        None)

            for waveDirection in sorted(spectrum.results[speed].keys()):
                waveDirectionsItem = self.addParent(
                    speedsItem, 0, "Wave direction: %4.2f" % waveDirection,
                    None)

                for kind in spectrum.results[speed][waveDirection].keys():
                    kindItem = self.addParent(waveDirectionsItem, 0, kind,
                                              None)

                    for variable in sorted(spectrum.results[speed]
                                           [waveDirection][kind].keys()):

                        #Dirty switch:
                        if spectrum.results[speed][waveDirection][kind][
                                variable].significantValue:
                            value = spectrum.results[speed][waveDirection][
                                kind][variable].significantValue
                        else:
                            value = spectrum.results[speed][waveDirection][
                                kind][variable].mean

                        variableItem = QtGui.QTreeWidgetItem(
                            kindItem, [variable, str(value)])

                        self.resultVariableDict[variableItem] = {}
                        self.resultVariableDict[variableItem]['speed'] = speed
                        self.resultVariableDict[variableItem][
                            'waveDirection'] = waveDirection
                        self.resultVariableDict[variableItem]['kind'] = kind
                        self.resultVariableDict[variableItem][
                            'variable'] = variable

                        variableItem.setExpanded(True)

        self.treeWidget.resizeColumnToContents(0)

    def copyResults(self):

        spectrum = self.resultsVariableDict[self.treeWidget.currentItem()]

        variableDictionary = {}

        for speed in sorted(spectrum.results.keys()):

            for waveDirection in sorted(spectrum.results[speed].keys()):

                for kind in spectrum.results[speed][waveDirection].keys():

                    for variable in sorted(spectrum.results[speed]
                                           [waveDirection][kind].keys()):

                        if kind == "addedResistance":
                            row = [
                                speed, waveDirection, spectrum.results[speed]
                                [waveDirection][kind][variable].mean
                            ]
                        else:
                            row = [
                                speed, waveDirection,
                                spectrum.results[speed][waveDirection][kind]
                                [variable].significantValue
                            ]

                        if variable not in variableDictionary:
                            variableDictionary[variable] = []

                        variableDictionary[variable].append(row)

        text = "Spectrum\t%s\n" % spectrum.getType()
        if spectrum.getType() == "ITTCSpectrum":
            text += "Hs\t%f\tTz\t%f\n" % (spectrum.Hs, spectrum.Tz)
        elif spectrum.getType() == "JonswapSpectrum":
            text += "Hs\t%f\tTp\t%f\n" % (spectrum.Hs, spectrum.Tp)
        elif spectrum.getType() == "FileSpectrum":
            text += "Hs\t%f\tTz\t%f\n" % (spectrum.Hs, spectrum.Tz)
        else:
            raise TypeError("Unknown spectrum: %s" % spectrum.getType())

        firstColumn = next(iter(variableDictionary.values()))

        text += "speed [knots]\twaveDirection [deg]\t"

        for variable in variableDictionary.keys():
            text += "%s\t" % variable

        text += "\n"

        numberOfRows = len(firstColumn)

        for row in range(numberOfRows):

            for column in firstColumn[row][0:-1]:
                text += "%f\t" % column

            for variable in variableDictionary.values():
                value = variable[row][-1]
                if value:
                    text += "%f\t" % value
                else:
                    text += " \t"

            text += "\n"

        QtGui.QApplication.instance().clipboard().setText(text)
        a = 1

    def save(self, filename):
        """Save the wave spectrum list, using pickle"""
        with open(filename, 'wb') as file:
            pickle.dump(self.waveSpectrums, file)

    def open(self, spectrumFileName):
        with open(spectrumFileName, 'rb') as file:
            waveSpectrums = pickle.load(file)

            for waveSpectrum in waveSpectrums:
                self.addSpectrum(waveSpectrum)


class AddSpectrumWindow(QtGui.QDialog):
    def __init__(self, parent=None, spectrum=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent

        self.setWindowTitle("Define Spectrum")
        self.setGeometry(300, 300, 300, 200)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        self.combo = QtGui.QComboBox(self)

        #This is a dictorinary will all the spectrum classes:
        self.Spectrums = {}
        self.Spectrums["Jonswap"] = JonswapSpectrumWindow
        self.Spectrums["ITTC"] = ITTCSpectrumWindow
        self.Spectrums["From file"] = FromFileSpectrumWindow

        for spectrumName in self.Spectrums.keys():
            self.combo.addItem(spectrumName)

        #combo.activated[str].connect(self.chooseSpectrum)
        self.grid.addWidget(self.combo, 0, 0, 1, 1)

        #Labels:
        nameLabel = QtGui.QLabel('Name of spectrum:')

        #Edit boxes:
        self.nameEdit = QtGui.QLineEdit()

        self.grid.addWidget(nameLabel, 1, 0, 1, 1)
        self.grid.addWidget(self.nameEdit, 1, 1, 1, 1)

        #Buttons:
        self.okButton = QtGui.QPushButton('OK', self)
        self.okButton.clicked.connect(self.ok)

        self.grid.addWidget(self.okButton, 0, 2, 1, 1)

        self.setLayout(self.grid)

        self.waveSpectrum = spectrum
        if spectrum:
            self.update(spectrum)

    def update(self, spectrum):
        """Updates the input to an existing spectrum"""
        self.nameEdit.setText(str(spectrum.name))

        #Search for the right spectrum type:
        counter = 0
        for Spectrum in self.Spectrums.values():
            if Spectrum().WaveSpectrum == type(spectrum):
                self.combo.setCurrentIndex(counter)
                break
            counter += 1
            if counter > len(self.Spectrums) - 1:
                raise ValueError('Gui for %s dos no exist' % spectrum.name)

    def ok(self):
        #if hasattr(self,'waveSpectrum'):
        #	self.accept()
        #else:
        #	self.chooseSpectrum()
        self.chooseSpectrum()
        self.accept()

    def chooseSpectrum(self):

        text = str(self.combo.currentText())

        #if text == "ITTC":
        #	spectrumWindow = ITTCSpectrumWindow(self)
        #elif text == "Jonswap":
        #	spectrumWindow = JonswapSpectrumWindow(self)
        #elif text == "From file":
        #	spectrumWindow = FromFileSpectrumWindow(self)

        #Create an instance of the spectrum class, defined by text:
        spectrumWindow = self.Spectrums[text](self, self.waveSpectrum)
        spectrumWindow.exec_()

        if hasattr(spectrumWindow, 'waveSpectrum'):
            self.waveSpectrum = spectrumWindow.waveSpectrum


class SpectrumWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent

        self.setWindowTitle("Define Spectrum")
        self.setGeometry(300, 300, 300, 200)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)


class ITTCSpectrumWindow(SpectrumWindow):
    def __init__(self, parent=None, spectrum=None):
        super(ITTCSpectrumWindow, self).__init__(parent)

        #Wave spectrum class used:
        self.WaveSpectrum = waveSpectrum.ITTCSpectrum

        if spectrum != None:
            Hs = spectrum.Hs
            Tz = spectrum.Tz
        else:
            Hs = 0
            Tz = 0

        #Labels:
        HsLabel = QtGui.QLabel('Hs [m]')
        TzLabel = QtGui.QLabel('Tz [s]')

        #Edit boxes:
        self.HsEdit = QtGui.QLineEdit(str(Hs))
        self.TzEdit = QtGui.QLineEdit(str(Tz))

        #Buttons:
        self.okButton = QtGui.QPushButton('OK', self)
        self.okButton.clicked.connect(self.ok)

        self.grid.addWidget(HsLabel, 2, 0, 1, 1)
        self.grid.addWidget(TzLabel, 3, 0, 1, 1)
        self.grid.addWidget(self.HsEdit, 2, 1, 1, 1)
        self.grid.addWidget(self.TzEdit, 3, 1, 1, 1)
        self.grid.addWidget(self.okButton, 4, 0, 1, 1)

        self.setLayout(self.grid)

        self.waveSpectrum = spectrum

    def ok(self):

        Hs = float(self.HsEdit.text())
        Tz = float(self.TzEdit.text())
        name = self.parent.nameEdit.text()

        if self.waveSpectrum:
            self.waveSpectrum.name = name
            self.waveSpectrum.Hs = Hs
            self.waveSpectrum.Tz = Tz
        else:
            self.waveSpectrum = self.WaveSpectrum(name, Hs, Tz)

        self.accept()


class JonswapSpectrumWindow(SpectrumWindow):
    def __init__(self, parent=None, spectrum=None):
        super(JonswapSpectrumWindow, self).__init__(parent)

        #Wave spectrum class used:
        self.WaveSpectrum = waveSpectrum.JonswapSpectrum

        if spectrum != None:
            Hs = spectrum.Hs
            Tp = spectrum.Tp
            gamma = sectrum.gamma
        else:
            Hs = 0
            Tp = 0
            gamma = 3.3

        #Labels:
        HsLabel = QtGui.QLabel('Hs [m]')
        TpLabel = QtGui.QLabel('Tp [s]')
        gammaLabel = QtGui.QLabel('gamma')

        #Edit boxes:
        self.HsEdit = QtGui.QLineEdit(str(Hs))
        self.TpEdit = QtGui.QLineEdit(str(Tp))
        self.gammaEdit = QtGui.QLineEdit(str(gamma))

        #Buttons:
        self.okButton = QtGui.QPushButton('OK', self)
        self.okButton.clicked.connect(self.ok)

        self.grid.addWidget(HsLabel, 2, 0, 1, 1)
        self.grid.addWidget(TpLabel, 3, 0, 1, 1)
        self.grid.addWidget(gammaLabel, 4, 0, 1, 1)

        self.grid.addWidget(self.HsEdit, 2, 1, 1, 1)
        self.grid.addWidget(self.TpEdit, 3, 1, 1, 1)
        self.grid.addWidget(self.gammaEdit, 4, 1, 1, 1)
        self.grid.addWidget(self.okButton, 5, 0, 1, 1)

        self.setLayout(self.grid)

        self.waveSpectrum = spectrum

    def ok(self):

        try:
            Hs = float(self.HsEdit.text())
        except:
            Hs = 1
        try:
            Tp = float(self.TpEdit.text())
        except:
            Tp = 10
        try:
            gamma = float(self.gammaEdit.text())
        except:
            gamma = 3.3

        name = self.parent.nameEdit.text()

        self.waveSpectrum = self.WaveSpectrum(name, Hs, Tp, gamma)
        self.accept()


class FromFileSpectrumWindow(SpectrumWindow):
    def __init__(self, parent=None, spectrum=None):
        super(FromFileSpectrumWindow, self).__init__(parent)

        #Wave spectrum class used:
        self.WaveSpectrum = waveSpectrum.FileSpectrum

        if spectrum:
            Hs = spectrum.Hs
            Tp = spectrum.Tp
            gamma = spectrum.gamma
        else:
            Hs = 0
            Tp = 0
            gamma = 3.3

        # set the shortcut ctrl+v for paste
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+v'),
                        self).activated.connect(self._handlePaste)

        # initially construct the visible table
        #This is a table where you can define your spectrum
        self.tv = QtGui.QTableWidget()
        self.tv.setRowCount(100)
        self.tv.setColumnCount(2)

        item = QtGui.QTableWidgetItem('frequency [rad/s]')
        self.tv.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem('S [m2*s]')
        self.tv.setHorizontalHeaderItem(1, item)
        self.tv.resizeColumnsToContents()

        #Labels:
        HsLabel = QtGui.QLabel('Hs [m]')
        TpLabel = QtGui.QLabel('Tp [s]')
        gammaLabel = QtGui.QLabel('gamma')

        #Edit boxes:
        self.HsEdit = QtGui.QLineEdit(str(Hs))

        self.TpEdit = QtGui.QLineEdit(str(Tp))

        self.gammaEdit = QtGui.QLineEdit()
        self.gammaEdit.setText(str(gamma))

        #Buttons:
        self.okButton = QtGui.QPushButton('OK', self)
        self.okButton.clicked.connect(self.ok)

        self.grid.addWidget(self.okButton, 5, 0, 1, 1)

        self.grid.addWidget(HsLabel, 2, 0, 1, 1)
        self.grid.addWidget(TpLabel, 3, 0, 1, 1)
        self.grid.addWidget(gammaLabel, 4, 0, 1, 1)

        self.grid.addWidget(self.HsEdit, 2, 1, 1, 1)
        self.grid.addWidget(self.TpEdit, 3, 1, 1, 1)
        self.grid.addWidget(self.gammaEdit, 4, 1, 1, 1)
        self.grid.addWidget(self.okButton, 5, 0, 1, 1)

        self.grid.addWidget(self.tv, 6, 0, 12, 3)

        self.setLayout(self.grid)

        self.waveSpectrum = spectrum

    def ok(self):

        Hs = float(self.HsEdit.text())
        Tp = float(self.TpEdit.text())
        gamma = float(self.gammaEdit.text())
        name = self.parent.nameEdit.text()

        frequencies = []
        Ss = []

        for row in range(self.tv.rowCount()):
            item = self.tv.item(row, 0)
            frequencies.append(float(item.text()))

            item = self.tv.item(row, 1)
            Ss.append(float(item.text()))

        self.waveSpectrum = self.WaveSpectrum(name, frequencies, Ss, Hs, Tp)
        self.accept()

    def _handlePaste(self):
        clipboard_text = QtGui.QApplication.instance().clipboard().text()

        clipboardString = str(clipboard_text)

        lines = clipboardString.splitlines()
        numberOfRows = len(lines)
        numberOfColumns = 2

        self.tv.setRowCount(numberOfRows)
        self.tv.setColumnCount(numberOfColumns)

        rowCounter = 0
        for row in clipboardString.splitlines():
            columnCounter = 0
            for column in row.split('\t'):
                if columnCounter < numberOfColumns:
                    item = QtGui.QTableWidgetItem(column)
                    self.tv.setItem(rowCounter, columnCounter, item)
                    columnCounter += 1

            rowCounter += 1

        self.tv.resizeColumnsToContents()
        self.tv.resizeRowsToContents()
