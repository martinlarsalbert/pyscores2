from PyQt4.QtCore import *
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from . import indata
import os.path
from . import output
import numpy as np
from . import plotWindow
import scipy.io


class ResultWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(ResultWidget, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle('ScoresII results')

        self.treeWidget = QtGui.QTreeWidget()
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 400, 800))
        self.treeWidget.setHeaderLabels(
            [' ', 'value', 'frequency', 'encounter frequency', 'wave length'])
        self.setWidget(self.treeWidget)

        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.treeWidget.customContextMenuRequested.connect(self.treePopup)

        self.actionCopy = QtGui.QAction("Copy", self)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPlot = QtGui.QAction("Plot", self)
        self.actionPlot.triggered.connect(self.plot)

        self.popMenu = QtGui.QMenu(self)
        self.popMenu.addAction(self.actionCopy)
        self.popMenu.addAction(self.actionPlot)

        self.treeItemDict = {}

    def showResults(self, resultPath):
        self.resultPath = resultPath
        self.scoresFile = output.OutputFile(self.resultPath)
        #Run bystrom correction for all added resistance raos:
        #self.scoresFile.runBystromCorrectionForAll()

        self.treeWidget.clear()
        self.fillTree(self.treeWidget.invisibleRootItem(),
                      self.scoresFile.results)

        self.show()

        a = 1

    def fillTree(self, parent, results):
        column = 0

        for speed in sorted(results.keys()):

            itemName = "Speed: %0.2f knots" % speed
            item = self.addParent(parent, column, itemName, 'data Clients')

            for waveAngle in sorted(results[speed].keys()):

                itemName = "Wave direction: %0.1f" % waveAngle

                item2 = self.addParent(item, column, itemName, 'data Clients')

                item3 = self.addChild(
                    item2, column, 'addedResistance',
                    results[speed][waveAngle].addedResistance)

                if results[speed][
                        waveAngle].lateralPlaneResponses.frequencies != None:
                    item3 = self.addChild(
                        item2, column, 'lateralPlaneResponses',
                        results[speed][waveAngle].lateralPlaneResponses)

                item3 = self.addChild(
                    item2, column, 'verticalPlaneResponses',
                    results[speed][waveAngle].verticalPlaneResponses)

                item3 = self.addChild(
                    item2, column, 'pointAccelerations',
                    results[speed][waveAngle].pointAccelerations)

        self.treeWidget.setColumnWidth(0, 200)

    def addParent(self, parent, column, title, data):
        item = QtGui.QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setExpanded(False)
        return item

    def addChild(self, parent, column, title, datas):

        item = self.addParent(parent, column, title, '')

        variables = vars(datas)

        for variable in variables.keys():
            if type(variables[variable]) == type(np.array([])) \
             and variable !="encounterFrequencies" and variable !="frequencies" and variable !="waveLengths":
                item2 = self.addParent(item, column, variable, '')

                self.treeItemDict[item2] = datas

                for value, frequency, encounterFrequency, waveLength in zip(
                        variables[variable], variables["frequencies"],
                        variables["encounterFrequencies"],
                        variables["waveLengths"]):
                    item3 = QtGui.QTreeWidgetItem(item2, [
                        ' ',
                        str(value),
                        str(frequency),
                        str(encounterFrequency),
                        str(waveLength)
                    ])
                    item3.setData(column, QtCore.Qt.UserRole, value)

        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.resizeColumnToContents(1)
        self.treeWidget.resizeColumnToContents(2)
        self.treeWidget.resizeColumnToContents(3)

        #item.setCheckState (column, QtCore.Qt.Unchecked)
        return item

    def handleChanged(self, item, column):
        if item.checkState(column) == QtCore.Qt.Checked:
            print("checked", item, item.text(column))
        if item.checkState(column) == QtCore.Qt.Unchecked:
            print("unchecked", item, item.text(column))

    def treePopup(self, point):

        if self.countChildrenLevels(self.treeWidget.currentItem()) == 1:

            self.popMenu.exec_(self.treeWidget.mapToGlobal(point))

    def countChildrenLevels(self, item, counter=0):
        child = item.child(0)
        if child == None:
            return counter
        else:
            counter += 1
            return self.countChildrenLevels(child, counter)

    def plot(self):

        thePlotWindow = plotWindow.PlotWindow(self.parent)

        values = []
        frequencys = []

        realCurrentItem = self.treeItemDict[self.treeWidget.currentItem()]
        variables = vars(realCurrentItem)
        quantity = str(self.treeWidget.currentItem().data(0, 0).toString())
        values = variables[quantity]
        frequencys = realCurrentItem.frequencies

        #if quantity == 'force':

        yLabel = "%s %s" % (self.treeWidget.currentItem().parent().data(
            0, 0).toString(), self.treeWidget.currentItem().data(0,
                                                                 0).toString())
        xLabel = "wave frequency [rad/s]"
        title = "%s %s %s" % (
            self.treeWidget.currentItem().parent().data(0, 0).toString(),
            self.treeWidget.currentItem().parent().parent().data(0,
                                                                 0).toString(),
            self.treeWidget.currentItem().parent().parent().parent().data(
                0, 0).toString())

        thePlotWindow.plot(frequencys, values, xLabel, yLabel, title)

    def copy(self):

        valueName = str(self.treeWidget.currentItem().parent().data(
            0, 0).toString())
        quantity = str(self.treeWidget.currentItem().data(0, 0).toString())
        waveDirection = str(
            self.treeWidget.currentItem().parent().parent().parent().data(
                0, 0).toString())
        speed = str(self.treeWidget.currentItem().parent().parent().data(
            0, 0).toString())

        text = "%s\n%s\n%s\n%s\n%s\t%s\t%s\t%s\n" % (
            valueName, quantity, waveDirection, speed, "value", "frequency",
            "encounterFrequency", "waveLength")

        for childIndex in range(self.treeWidget.currentItem().childCount()):
            child = self.treeWidget.currentItem().child(childIndex)

            data = child.data(1, 0)
            value = data.toFloat()[0]
            data = child.data(2, 0)
            frequency = data.toFloat()[0]
            data = child.data(3, 0)
            encounterFrequency = data.toFloat()[0]
            data = child.data(4, 0)
            waveLength = data.toFloat()[0]

            text += "%f\t%f\t%f\t%f\n" % (value, frequency, encounterFrequency,
                                          waveLength)

        QtGui.QApplication.instance().clipboard().setText(text)

    def exportRAW(self, exportPath=None):
        """This function exports only the Added Resistnace """

        if hasattr(self, 'scoresFile'):
            if exportPath == None:
                exportPath = QtGui.QFileDialog.getSaveFileName(
                    self, 'Export file', "c:/", "RAO (*.mat)")

            exportPath = os.path.normpath(str(exportPath))

            Lpp = self.scoresFile.geometry.Lpp
            B = self.scoresFile.geometry.B

            matrix = []
            for speed, speedResults in self.scoresFile.results.items():
                for waveAngle, waveDirResult in list(speedResults.items()):

                    #waveAngle = waveDirResult.waveAngle
                    #speed = waveDirResult.speed

                    for addedResistance, waveLength in zip(
                            waveDirResult.addedResistance.forces,
                            waveDirResult.addedResistance.waveLengths):

                        lambdaOverLpp = waveLength / Lpp
                        rho = 1025.0
                        g = 9.81
                        RAOaddresNonDim = addedResistance * 1000 / (rho * g *
                                                                    B**2 / Lpp)

                        matrix.append(
                            [waveAngle, speed, lambdaOverLpp, RAOaddresNonDim])

            rawRAOs = np.array(matrix)

            try:
                scipy.io.savemat(exportPath, mdict={'rawRAOs': rawRAOs})
            except:
                self.parent.statusBar().showMessage('RAO export error')
            else:
                self.parent.statusBar().showMessage('RAO exported to: %s' %
                                                    exportPath)

    def exportRAO(self, exportPath=None):
        """This function exports All the RAOs """

        if hasattr(self, 'scoresFile'):
            if exportPath == None:
                exportPath = QtGui.QFileDialog.getSaveFileName(
                    self, 'Export file', "c:/", "RAO (*.mat)")

            exportPath = os.path.normpath(str(exportPath))

            Lpp = self.scoresFile.geometry.Lpp
            B = self.scoresFile.geometry.B

            numberOfSpeeds = len(self.scoresFile.results)
            numberOfWaveDirections = 1
            numberOfRAOs = 3  #Set the number of possible RAOs

            for speed, speedResults in self.scoresFile.results.items():
                tempNumberOfWaveDirections = len(speedResults)
                if tempNumberOfWaveDirections > numberOfWaveDirections:
                    numberOfWaveDirection = tempNumberOfWaveDirections

            #Simulate a Matlab struct in Python:
            dt = [('waveDirection', 'f8'), ('title', 'S20'),
                  ('nominalSpeed', 'f8'), ('x', 'O8'), ('yTitle', 'S20'),
                  ('y', 'O8')]
            RAOs = np.zeros(
                (numberOfWaveDirections, numberOfSpeeds, numberOfRAOs),
                dtype=dt)

            speedCounter = 0
            for speed, speedResults in self.scoresFile.results.items():
                waveAngleCounter = 0
                for waveAngle, waveDirResult in list(speedResults.items()):

                    #for addedResistance,waveLength in zip(waveDirResult.addedResistance.forces,waveDirResult.addedResistance.waveLengths):
                    #
                    #	lambdaOverLpp = waveLength / Lpp

                    rho = 1000.0
                    g = 9.81
                    RAOaddresNonDim = waveDirResult.addedResistance.forces * 1000 / (
                        rho * g * B**2 / Lpp)

                    lambdaOverLpp = waveDirResult.addedResistance.waveLengths / Lpp
                    RAOs[waveAngleCounter][speedCounter][0][
                        'waveDirection'] = waveAngle
                    RAOs[waveAngleCounter][speedCounter][0][
                        'nominalSpeed'] = speed
                    RAOs[waveAngleCounter][speedCounter][0][
                        'x'] = lambdaOverLpp
                    RAOs[waveAngleCounter][speedCounter][0][
                        'y'] = RAOaddresNonDim
                    RAOs[waveAngleCounter][speedCounter][0][
                        'title'] = 'Added resistance'
                    RAOs[waveAngleCounter][speedCounter][0][
                        'yTitle'] = 'addedResistance'

                    lambdaOverLpp = waveDirResult.verticalPlaneResponses.waveLengths / Lpp
                    RAOs[waveAngleCounter][speedCounter][1][
                        'waveDirection'] = waveAngle
                    RAOs[waveAngleCounter][speedCounter][1][
                        'nominalSpeed'] = speed
                    RAOs[waveAngleCounter][speedCounter][1][
                        'x'] = lambdaOverLpp
                    RAOs[waveAngleCounter][speedCounter][1][
                        'y'] = waveDirResult.verticalPlaneResponses.heaveAmplitude
                    RAOs[waveAngleCounter][speedCounter][1]['title'] = 'Heave'
                    RAOs[waveAngleCounter][speedCounter][1]['yTitle'] = 'heave'

                    lambdaOverLpp = waveDirResult.verticalPlaneResponses.waveLengths / Lpp
                    RAOs[waveAngleCounter][speedCounter][2][
                        'waveDirection'] = waveAngle
                    RAOs[waveAngleCounter][speedCounter][2][
                        'nominalSpeed'] = speed
                    RAOs[waveAngleCounter][speedCounter][2][
                        'x'] = lambdaOverLpp

                    pitchScoresII = waveDirResult.verticalPlaneResponses.pitchAmplitude  # pitch / h [deg/m]
                    pitchScoresII = waveDirResult.verticalPlaneResponses.pitchAmplitude
                    lamda = waveDirResult.verticalPlaneResponses.waveLengths
                    y = pitchScoresII * lamda / 360.0  # y = pitchRad*lambda / (2*pi*Xia)

                    RAOs[waveAngleCounter][speedCounter][2]['y'] = y

                    RAOs[waveAngleCounter][speedCounter][2]['title'] = 'Pitch'
                    RAOs[waveAngleCounter][speedCounter][2]['yTitle'] = 'pitch'

                    RAOsMatrix = np.array(RAOs)

                    waveAngleCounter += 1

                speedCounter += 1

            try:
                scipy.io.savemat(exportPath, mdict={'RAOs': RAOsMatrix})
            except:
                self.parent.statusBar().showMessage('RAO export error')
            else:
                self.parent.statusBar().showMessage('RAO exported to: %s' %
                                                    exportPath)
