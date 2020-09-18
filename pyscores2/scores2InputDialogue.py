from PyQt4.QtCore import *
import PyQt4.QtGui as QtGui
from . import indata
import os.path
from . import runScores2
from . import resultGUI
from . import waveSpectrumGUI
import copy
from . import waveSpectrum
from . import xml_hydrostatics


class Widget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent

        self.setGeometry(20, 10, 40, 40)

        #Create a grid layout:
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        # initially construct the visible table
        self.tv = QtGui.QTableWidget()
        self.tv.setRowCount(21)
        self.tv.setColumnCount(3)
        item = QtGui.QTableWidgetItem('B [m]')
        self.tv.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem('Cscores')
        self.tv.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem('T [m]')
        self.tv.setHorizontalHeaderItem(2, item)
        self.tv.resizeColumnsToContents()

        # set the shortcut ctrl+v for paste
        #QtGui.QShortcut(QtGui.QKeySequence('Ctrl+v'),self).activated.connect(self._handlePaste)

        self.grid.addWidget(self.tv, 0, 0, 12, 1)

        #Labels:
        projectName = QtGui.QLabel('Project Name')
        lpp = QtGui.QLabel('Lpp [m]')
        displacement = QtGui.QLabel('Displacement [m3]')
        lcb = QtGui.QLabel('lcb [%]')
        kyy = QtGui.QLabel('kyy [m]')
        kxx = QtGui.QLabel('kxx [m]')
        rho = QtGui.QLabel('rho [kg/m3]')
        g = QtGui.QLabel('g [m/s2]')
        zcg = QtGui.QLabel('zcg [m]')
        zcgDescription = QtGui.QLabel(
            '(CG meassured from WL, positive upwards)')
        partOfCriticalRollDamping = QtGui.QLabel(
            'Part of critical roll damping [-]')
        min = QtGui.QLabel('min')
        max = QtGui.QLabel('max')
        increment = QtGui.QLabel('increment')
        speeds = QtGui.QLabel('speed [knots]')
        waveDirections = QtGui.QLabel('wave directions [deg]')
        waveFrequencies = QtGui.QLabel('wave frequencies [rad/s]')

        #Edit boxes:

        self.projectNameEdit = QtGui.QLineEdit(
            parent.scores2Indata.projectName)
        self.lppEdit = QtGui.QLineEdit(str(parent.scores2Indata.lpp))
        self.displacementEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.displacement))
        self.lcbEdit = QtGui.QLineEdit(str(parent.scores2Indata.lcb))
        self.kyyEdit = QtGui.QLineEdit(str(parent.scores2Indata.kyy))
        self.kxxEdit = QtGui.QLineEdit(str(parent.scores2Indata.kxx))
        self.rhoEdit = QtGui.QLineEdit(str(parent.scores2Indata.rho))
        self.gEdit = QtGui.QLineEdit(str(parent.scores2Indata.g))
        self.zcgEdit = QtGui.QLineEdit(str(parent.scores2Indata.zcg))
        self.partOfCriticalRollDampingEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.partOfCriticalRollDamping))
        self.speedMinEdit = QtGui.QLineEdit(str(parent.scores2Indata.speedMin))
        self.speedMaxEdit = QtGui.QLineEdit(str(parent.scores2Indata.speedMax))
        self.speedIncrementEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.speedIncrement))
        self.waveDirectionMinEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionMin))
        self.waveDirectionMaxEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionMax))
        self.waveDirectionIncrementEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionIncrement))
        self.waveDirectionMinEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionMin))
        self.waveDirectionMaxEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionMax))
        self.waveDirectionIncrementEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveDirectionIncrement))
        self.waveFrequenciesMinEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveFrequenciesMin))
        self.waveFrequenciesMaxEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveFrequenciesMax))
        self.waveFrequenciesIncrementEdit = QtGui.QLineEdit(
            str(parent.scores2Indata.waveFrequenciesIncrement))

        #Add the stuff to the grid:
        self.grid.addWidget(projectName, 0, 2, 1, 3)
        self.grid.addWidget(lpp, 1, 2, 1, 1)
        self.grid.addWidget(displacement, 2, 2, 1, 1)
        self.grid.addWidget(lcb, 3, 2, 1, 1)
        self.grid.addWidget(kyy, 4, 2, 1, 1)
        self.grid.addWidget(kxx, 5, 2, 1, 1)
        self.grid.addWidget(rho, 6, 2, 1, 1)
        self.grid.addWidget(g, 7, 2, 1, 1)
        self.grid.addWidget(zcg, 8, 2, 1, 1)
        self.grid.addWidget(zcgDescription, 8, 4, 1, 1)
        self.grid.addWidget(partOfCriticalRollDamping, 9, 2, 1, 1)
        self.grid.addWidget(min, 10, 3, 1, 1)
        self.grid.addWidget(max, 10, 4, 1, 1)
        self.grid.addWidget(increment, 10, 5, 1, 1)
        self.grid.addWidget(speeds, 11, 2, 1, 1)
        self.grid.addWidget(waveDirections, 12, 2, 1, 1)
        self.grid.addWidget(waveFrequencies, 13, 2, 1, 1)

        self.grid.addWidget(self.projectNameEdit, 0, 3, 1, 1)
        self.grid.addWidget(self.lppEdit, 1, 3, 1, 1)
        self.grid.addWidget(self.displacementEdit, 2, 3, 1, 1)
        self.grid.addWidget(self.lcbEdit, 3, 3, 1, 1)
        self.grid.addWidget(self.kyyEdit, 4, 3, 1, 1)
        self.grid.addWidget(self.kxxEdit, 5, 3, 1, 1)
        self.grid.addWidget(self.rhoEdit, 6, 3, 1, 1)
        self.grid.addWidget(self.gEdit, 7, 3, 1, 1)
        self.grid.addWidget(self.zcgEdit, 8, 3, 1, 1)
        self.grid.addWidget(self.partOfCriticalRollDampingEdit, 9, 3, 1, 1)
        self.grid.addWidget(self.speedMinEdit, 11, 3, 1, 1)
        self.grid.addWidget(self.speedMaxEdit, 11, 4, 1, 1)
        self.grid.addWidget(self.speedIncrementEdit, 11, 5, 1, 1)
        self.grid.addWidget(self.waveDirectionMinEdit, 12, 3, 1, 1)
        self.grid.addWidget(self.waveDirectionMaxEdit, 12, 4, 1, 1)
        self.grid.addWidget(self.waveDirectionIncrementEdit, 12, 5, 1, 1)
        self.grid.addWidget(self.waveFrequenciesMinEdit, 13, 3, 1, 1)
        self.grid.addWidget(self.waveFrequenciesMaxEdit, 13, 4, 1, 1)
        self.grid.addWidget(self.waveFrequenciesIncrementEdit, 13, 5, 1, 1)

        self.setLayout(self.grid)
        self.tv.show()

    # paste the value
    def _handlePaste(self):
        clipboard_text = QtGui.QApplication.instance().clipboard().text()

        clipboardString = str(clipboard_text)

        lines = clipboardString.splitlines()
        numberOfRows = len(lines)
        numberOfColumns = 3

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

    def displayData(self):
        #Table data:
        numberOfRows = len(self.parent.scores2Indata.bs)
        numberOfColumns = 3

        self.tv.setRowCount(numberOfRows)
        self.tv.setColumnCount(numberOfColumns)

        rowCounter = 0
        for b, cScores, t in zip(self.parent.scores2Indata.bs,
                                 self.parent.scores2Indata.cScores,
                                 self.parent.scores2Indata.ts):
            item = QtGui.QTableWidgetItem(str(b))
            self.tv.setItem(rowCounter, 0, item)
            item = QtGui.QTableWidgetItem(str(cScores))
            self.tv.setItem(rowCounter, 1, item)
            item = QtGui.QTableWidgetItem(str(t))
            self.tv.setItem(rowCounter, 2, item)
            rowCounter += 1

        self.tv.resizeColumnsToContents()
        self.tv.resizeRowsToContents()

        #Other data:
        self.projectNameEdit.setText(self.parent.scores2Indata.projectName)
        self.lppEdit.setText(str(self.parent.scores2Indata.lpp))
        self.displacementEdit.setText(
            str(self.parent.scores2Indata.displacement))
        self.lcbEdit.setText(str(self.parent.scores2Indata.lcb))
        self.kyyEdit.setText(str(self.parent.scores2Indata.kyy))
        self.kxxEdit.setText(str(self.parent.scores2Indata.kxx))
        self.rhoEdit.setText(str(self.parent.scores2Indata.rho))
        self.gEdit.setText(str(self.parent.scores2Indata.g))
        self.zcgEdit.setText(str(self.parent.scores2Indata.zcg))
        self.partOfCriticalRollDampingEdit.setText(
            str(self.parent.scores2Indata.partOfCriticalRollDamping))
        self.speedMinEdit.setText(str(self.parent.scores2Indata.speedMin))
        self.speedMaxEdit.setText(str(self.parent.scores2Indata.speedMax))
        self.speedIncrementEdit.setText(
            str(self.parent.scores2Indata.speedIncrement))
        self.waveDirectionMinEdit.setText(
            str(self.parent.scores2Indata.waveDirectionMin))
        self.waveDirectionMaxEdit.setText(
            str(self.parent.scores2Indata.waveDirectionMax))
        self.waveDirectionIncrementEdit.setText(
            str(self.parent.scores2Indata.waveDirectionIncrement))
        self.waveFrequenciesMinEdit.setText(
            str(self.parent.scores2Indata.waveFrequenciesMin))
        self.waveFrequenciesMaxEdit.setText(
            str(self.parent.scores2Indata.waveFrequenciesMax))
        self.waveFrequenciesIncrementEdit.setText(
            str(self.parent.scores2Indata.waveFrequenciesIncrement))

    def getData(self):

        #tempIndata = scores2Indata.Scores2Indata()
        tempIndata = copy.copy(self.parent.scores2Indata)

        tempIndata.bs = []
        tempIndata.cScores = []
        tempIndata.ts = []

        for row in range(self.tv.rowCount()):

            item = self.tv.item(row, 0)
            if item:
                tempIndata.bs.append(float(item.text()))
            else:
                tempIndata.bs.append(0.0)

            item = self.tv.item(row, 1)
            if item:
                tempIndata.cScores.append(float(item.text()))
            else:
                tempIndata.cScores.append(0.0)

            item = self.tv.item(row, 2)
            if item:
                tempIndata.ts.append(float(item.text()))
            else:
                tempIndata.ts.append(0.0)

        #Other data:
        tempIndata.projectName = self.projectNameEdit.text()
        try:
            tempIndata.lpp = float(self.lppEdit.text())
        except:
            tempIndata.lpp = 0.0
        try:
            tempIndata.displacement = float(self.displacementEdit.text())
        except:
            tempIndata.displacement = 0.0
        try:
            tempIndata.lcb = float(self.lcbEdit.text())
        except:
            tempIndata.lcb = 0.0
        try:
            tempIndata.kyy = float(self.kyyEdit.text())
        except:
            tempIndata.kyy = 0.0
        try:
            tempIndata.kxx = float(self.kxxEdit.text())
        except:
            tempIndata.kxx = 0.0
        try:
            tempIndata.rho = float(self.rhoEdit.text())
            if abs(rho) < 10:
                messageBox = QtGui.QErrorMessage(self)
                messageBox.showMessage(
                    "rho is to small. It should be expressed in [kg/m3]")

        except:
            tempIndata.g = 1025
        try:
            tempIndata.g = float(self.gEdit.text())
        except:
            tempIndata.g = 9.81
        try:
            tempIndata.zcg = float(self.zcgEdit.text())
        except:
            tempIndata.zcg = 0.0
        try:
            tempIndata.partOfCriticalRollDamping = float(
                self.partOfCriticalRollDampingEdit.text())
        except:
            tempIndata.partOfCriticalRollDamping = 0.0
        try:
            tempIndata.speedMin = float(self.speedMinEdit.text())
        except:
            tempIndata.speedMin = 0.0
        try:
            tempIndata.speedMax = float(self.speedMaxEdit.text())
        except:
            tempIndata.speedMax = 0.0
        try:
            tempIndata.speedIncrement = float(self.speedIncrementEdit.text())
        except:
            tempIndata.speedIncrement = 0.0
        try:
            tempIndata.waveDirectionMin = float(
                self.waveDirectionMinEdit.text())
        except:
            tempIndata.waveDirectionMin = 0.0
        try:
            tempIndata.waveDirectionMax = float(
                self.waveDirectionMaxEdit.text())
        except:
            tempIndata.waveDirectionMax = 0.0
        try:
            tempIndata.waveDirectionIncrement = float(
                self.waveDirectionIncrementEdit.text())
        except:
            tempIndata.waveDirectionIncrement = 0.0

        try:
            tempIndata.waveFrequenciesMin = float(
                self.waveFrequenciesMinEdit.text())
        except:
            tempIndata.waveFrequenciesMin = 0.0
        try:
            tempIndata.waveFrequenciesMax = float(
                self.waveFrequenciesMaxEdit.text())
        except:
            tempIndata.waveFrequenciesMax = 0.0
        try:
            tempIndata.waveFrequenciesIncrement = float(
                self.waveFrequenciesIncrementEdit.text())
        except:
            tempIndata.waveFrequenciesIncrement = 0.0

        #Append this indata to the undo\redo list:
        self.updateIndata(tempIndata)

    def updateIndata(self, tempIndata):

        #Append this indata to the undo\redo list:
        #Has any data been modified?
        variables = vars(self.parent.scores2Indata)
        same = True
        for varname in variables:
            if hasattr(tempIndata, varname):
                if self.parent.scores2Indata.__dict__[
                        varname] != tempIndata.__dict__[varname]:
                    same = False
                    break
        if not same:
            self.parent.undoIndex += 1
            self.parent.scores2IndataList.append(tempIndata)
            self.parent.scores2Indata = tempIndata


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):

        self.setWindowTitle('ScoresII input')
        self.setWindowIcon(QtGui.QIcon('sspa.gif'))

        self.setGeometry(300, 300, 800, 800)

        self.savePath = ""

        #This is a list with the various instances of the scores2Indata class:
        #This list enables the posibility to av a undo redo function using instances in this list
        self.scores2IndataList = []
        self.undoIndex = 0

        #Define an instance of the scoresII indata class:
        self.scores2Indata = indata.Indata()
        self.scores2IndataList.append(self.scores2Indata)

        self.w = Widget(self)
        self.setCentralWidget(self.w)

        self.resultWidget = resultGUI.ResultWidget(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.resultWidget)

        self.waveSpectrumWidget = waveSpectrumGUI.waveSpectrumWidget(self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.waveSpectrumWidget)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.jpg'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        undoAction = QtGui.QAction('&Undo', self)
        undoAction.setShortcut('Ctrl+Z')
        undoAction.setStatusTip('Undo')
        undoAction.triggered.connect(self.undo)

        redoAction = QtGui.QAction('&Redo', self)
        redoAction.setShortcut('Ctrl+Y')
        redoAction.setStatusTip('Redo')
        redoAction.triggered.connect(self.redo)

        pasteAction = QtGui.QAction('&Paste', self)
        pasteAction.setShortcut('Ctrl+V')
        pasteAction.setStatusTip('Paste values')
        pasteAction.triggered.connect(self.w._handlePaste)

        saveAction = QtGui.QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save as scores.in')
        saveAction.triggered.connect(self.save)

        saveAsAction = QtGui.QAction('&SaveAs', self)
        saveAsAction.setShortcut('Ctrl+Alt+S')
        saveAsAction.setStatusTip('Save As as scores.in')
        saveAsAction.triggered.connect(self.saveAs)

        openAction = QtGui.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open scores.in')
        openAction.triggered.connect(self.open)

        importAction = QtGui.QAction('&Import XML', self)
        importAction.setShortcut('Ctrl+I')
        importAction.setStatusTip('Import data from hydrostatics XML file')
        importAction.triggered.connect(self.importXML)

        exportRAWAction = QtGui.QAction('&ExportRAW', self)
        exportRAWAction.setStatusTip('Export Added Resistance RAO only')
        exportRAWAction.triggered.connect(self.exportRAW)

        exportRAOAction = QtGui.QAction('&ExportRAO', self)
        exportRAOAction.setStatusTip('Export All the RAOs')
        exportRAOAction.triggered.connect(self.exportRAO)

        runScores2Action = QtGui.QAction(QtGui.QIcon('run.jpg'),
                                         'Run ScoresII', self)
        runScores2Action.setShortcut('Ctrl+R')
        runScores2Action.setStatusTip('Run ScoresII')
        runScores2Action.triggered.connect(self.runScores2)

        optionsAction = QtGui.QAction('Options', self)
        optionsAction.setShortcut('Ctrl+O')
        optionsAction.setStatusTip('Run Options')
        optionsAction.triggered.connect(self.openOptions)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(importAction)
        fileMenu.addAction(exportRAWAction)
        fileMenu.addAction(exportRAOAction)
        fileMenu.addAction(exitAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)
        editMenu.addAction(pasteAction)

        editMenu = menubar.addMenu('&Run')
        editMenu.addAction(optionsAction)
        editMenu.addAction(runScores2Action)

        self.toolbar = self.addToolBar('Run')
        self.toolbar.addAction(runScores2Action)

        self.w.show()
        self.statusBar().showMessage('Ready')
        self.show()

    def open(self):

        try:
            file = open('oldDir.txt', 'r')
            resentFile = file.readline()
            file.close()
        except IOError:
            resentFile = 'c:/'

        if not os.path.exists(resentFile):
            resentFile = 'c:/'

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                                                  resentFile,
                                                  "ScoresII in (*.in)")
        #Load indata from file:
        if os.path.exists(fname):

            #Append this indata to the undo\redo list:
            tempIndata = indata.Indata()
            tempIndata.open(fname)

            self.w.updateIndata(tempIndata)

            #Update with the loaded data:
            self.w.displayData()

            file = open('oldDir.txt', 'w')
            file.write(fname)
            file.close()

            self.savePath = fname

            #Are there spectra present in the indata?
            if tempIndata.runOptions["ID"] == 0:
                #Regular waves
                pass
            elif tempIndata.runOptions["ID"] == 1:
                #Neuman spectra
                pass
            elif tempIndata.runOptions["ID"] == 2:
                #PM spectra
                pass
            elif tempIndata.runOptions["ID"] == 3:
                #Two parameter spectra
                pass
            elif tempIndata.runOptions["ID"] == 4:
                #Tabulated spectra
                pass
            elif tempIndata.runOptions["ID"] == 5:
                #Bretschneider spectra
                pass
            elif tempIndata.runOptions["ID"] == 6:
                #Jonswap spectra
                for Hs, Tp in zip(tempIndata.H33s, tempIndata.Tps):
                    newSpectrum = waveSpectrum.JonswapSpectrum(
                        "NoName", Hs, Tp)
                    self.waveSpectrumWidget.addSpectrum(newSpectrum)

            #Are there spectrum files present?
            parts = os.path.splitext(str(fname))
            spectrumFileName = parts[0] + ".spe"

            if os.path.exists(spectrumFileName):
                self.waveSpectrumWidget.open(spectrumFileName)

    def save(self):
        self.w.getData()

        if self.savePath == "":
            self.savePath = str(
                QtGui.QFileDialog.getSaveFileName(
                    self, 'Save file',
                    str(self.scores2Indata.projectName) + ".in",
                    "ScoresII in (*.in)"))

        self.scores2Indata.save(self.savePath,
                                self.waveSpectrumWidget.waveSpectrums)

        #Save the spectrums into a separate file (since the Scores indata file format is not enought for this):
        parts = os.path.splitext(str(self.savePath))
        spectrumFileName = parts[0] + ".spe"
        self.waveSpectrumWidget.save(spectrumFileName)

    def saveAs(self, indataPath):
        self.w.getData()

        self.savePath = QtGui.QFileDialog.getSaveFileName(
            self, 'Save file as', "c:/", "ScoresII in (*.in)")
        self.scores2Indata.save(self.savePath,
                                self.waveSpectrumWidget.waveSpectrums)

    def runScores2(self):

        #Check if the table has been filled in to verify if it is worth running ScoresII
        if self.w.tv.item(0, 0) != None:

            filename = "temp"
            tempIndataPath = os.path.abspath(filename + ".in")
            tempOutdataPath = os.path.abspath(filename + ".out")

            if os.path.exists(tempOutdataPath):
                os.remove(tempOutdataPath)

            self.w.getData()
            self.scores2Indata.save(tempIndataPath,
                                    self.waveSpectrumWidget.waveSpectrums)
            calculation = runScores2.Calculation(tempIndataPath,
                                                 os.path.abspath(""))
            calculation.run()

            #Was the calculation succesfull?
            successful = False
            if os.path.exists(tempOutdataPath):
                if os.path.getsize(tempOutdataPath) > 10**4:
                    successful = True

            if successful:
                self.statusBar().showMessage(
                    'The ScoresII calculation completed')
                self.resultWidget.showResults(tempOutdataPath)

                #Assign the result to the wave spectrum widget also:
                self.waveSpectrumWidget.scoresFile = self.resultWidget.scoresFile

                if len(self.resultWidget.scoresFile.irregularResults) > 0:
                    #There is an irregular sea result that should be inserted into a spectrum:
                    wantedSpectrumID = int(
                        self.scores2Indata.runOptions["ID"].getValue())
                    counter = 0
                    counter2 = 0
                    for waveSpectrum in self.waveSpectrumWidget.waveSpectrums:

                        if waveSpectrum.scoresFileID == wantedSpectrumID:
                            if counter <= 5:  #Max 5 spectra alowed in scoresII
                                spectrumIndex = self.resultWidget.scoresFile.spectrumIndexList[
                                    counter]
                                waveSpectrum.results = self.resultWidget.scoresFile.irregularResults[
                                    spectrumIndex]

                                #Insert this result into the GUI:
                                for item, no in self.waveSpectrumWidget.spectrumItemDict.items(
                                ):
                                    if no == counter2:
                                        self.waveSpectrumWidget.addResult(
                                            item, waveSpectrum,
                                            'ScoresII Result')

                                counter += 1
                            else:
                                break

                        counter2 += 1

            else:
                errorCode, errorDescription = calculation.parse_error()

                for cScores in self.scores2Indata.cScores:
                    if cScores > 0.99:
                        errorDescription += " cScores > 1 can also be a problem"
                        break

                messageBox = QtGui.QErrorMessage(self)
                messageBox.showMessage(
                    "The ScoresII calculation was not successful! Error No.%s %s"
                    % (errorCode, errorDescription))

    def exportRAW(self):
        self.resultWidget.exportRAW()

    def exportRAO(self):
        self.resultWidget.exportRAO()

    def undo(self):
        if self.undoIndex > 0:
            self.undoIndex -= 1
            self.scores2Indata = self.scores2IndataList[self.undoIndex]
            #Update display data:
            self.w.displayData()

    def redo(self):
        if self.undoIndex < (len(self.scores2IndataList) - 1):
            self.undoIndex += 1
            self.scores2Indata = self.scores2IndataList[self.undoIndex]
            #Update display data:
            self.w.displayData()

    def openOptions(self):
        """Opens the option dialogue"""
        self.optionDialog = OptionsDialog(self)
        self.optionDialog.exec_()

    def importXML(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '',
                                                  "Hydrostatics (*.xml)")

        #fname = 'S:/2014/20147149-HHIC_5k_LNGC/projekt/arbetsmapp/Sim/Fartygsmodeller/Hydrostatics/HHIC_5k_ScoresData.xml'

        #Load indata from file:
        if os.path.exists(fname):

            hydrostatics = xml_hydrostatics.Parser(fname)

            #Take copy of current indata:
            tempIndata = copy.copy(self.scores2Indata)

            #Open a dialogue to chose wich condition from the XML file that should be loaded:
            conditionDialog = ConditionDialog(self, hydrostatics)
            conditionDialog.exec_()

            conditionName = conditionDialog.conditionName

            #Extract XML data to scores2Indata format:
            updatedTempIndata = hydrostatics.convertToScores2Indata(
                tempIndata=tempIndata, conditionName=conditionName)

            #Send this to GUI:
            self.scores2Indata = updatedTempIndata
            self.scores2IndataList.append(self.scores2Indata)
            self.w.displayData()

            a = 1

        else:
            messageBox.showMessage("Hydrostatics file does not exist")


class OptionsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent

        self.setWindowTitle("Run Options")
        self.setGeometry(300, 300, 300, 200)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        rowCounter = 0
        self.inputItems = {}
        for optionID in self.parent.scores2Indata.runOptionTags:
            option = self.parent.scores2Indata.runOptions[optionID]

            #Labels:
            label = QtGui.QLabel(option.description)
            self.grid.addWidget(label, rowCounter, 0, 1, 1)

            #Input item (either edit or radiobuttons):
            if option.alternatives:
                buttonGroup = QtGui.QButtonGroup(self)
                columnCounter = 0
                for alternative in option.alternatives:
                    radioButton = QtGui.QRadioButton(alternative.description,
                                                     self)
                    radioButton.setDown(alternative.getValue())

                    self.grid.addWidget(radioButton, rowCounter,
                                        1 + columnCounter, 1, 1)
                    buttonGroup.addButton(radioButton)
                    columnCounter += 1
                inputItem = buttonGroup
            else:
                #No alternatives
                #Edit boxes:
                inputItem = QtGui.QLineEdit(str(option.getValue()))
                self.grid.addWidget(inputItem, rowCounter, 1, 1, 1)

            self.inputItems[optionID] = inputItem

            rowCounter += 1

        self.setLayout(self.grid)

    def closeEvent(self, QCloseEvent):
        for optionID in self.parent.scores2Indata.runOptionTags:
            inputItem = self.inputItems[optionID]

            if type(inputItem) == type(QtGui.QLineEdit()):
                self.parent.scores2Indata.runOptions[optionID].set_value(
                    int(inputItem.text()))
            elif type(inputItem) == type(QtGui.QButtonGroup()):
                counter = 0
                for radioButton in inputItem.buttons():
                    if radioButton.isChecked():
                        self.parent.scores2Indata.runOptions[
                            optionID].set_value(counter)
                        break
                    counter += 1

        self.accept()


class ConditionDialog(QtGui.QDialog):
    def __init__(self, parent=None, hydrostatics=None):
        QtGui.QWidget.__init__(self, parent)

        self.parent = parent
        self.hydrostatics = hydrostatics

        self.setWindowTitle("Condition Options")
        self.setGeometry(300, 300, 100, 100)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        rowCounter = 0

        #Labels:
        descriptionLabel = QtGui.QLabel('Choose condition to load:')
        self.grid.addWidget(descriptionLabel, rowCounter, 0, 1, 1)

        #Combo box:
        self.conditionsComboBox = QtGui.QComboBox(parent=self)

        for condition in self.hydrostatics.conditions.values():
            self.conditionsComboBox.addItem(condition.Name)

        self.grid.addWidget(self.conditionsComboBox, rowCounter, 1, 1, 1)

        #Ok button:
        self.okButton = QtGui.QPushButton("Ok")
        self.okButton.clicked.connect(self.closeEvent)

        self.grid.addWidget(self.okButton, rowCounter, 2, 1, 1)

        #Labels:
        rowCounter += 1

        self.TALabel = QtGui.QLabel('')
        self.grid.addWidget(self.TALabel, rowCounter, 0, 1, 1)
        rowCounter += 1

        self.TFLabel = QtGui.QLabel('')
        self.grid.addWidget(self.TFLabel, rowCounter, 0, 1, 1)

        self.setLayout(self.grid)

        self.conditionsComboBox.currentIndexChanged.connect(self.updateTATF)

        self.updateTATF()

    def closeEvent(self, QCloseEvent):

        self.accept()

    def updateTATF(self):

        self.conditionName = str(self.conditionsComboBox.currentText())
        condition = self.hydrostatics.conditions[self.conditionName]

        TA = condition.TA
        TF = condition.TF

        TALabelText = "TA = %f [m]" % TA
        TFLabelText = "TF = %f [m]" % TA

        self.TALabel.setText(TALabelText)
        self.TFLabel.setText(TFLabelText)

        a = 1


app = QtGui.QApplication([])
mainWindow = MainWindow()
app.exec_()
