from PyQt4 import QtGui, QtCore
import numpy as np

HORIZONTAL_HEADERS = ("", "Value", "Frequency", "Encounter Frequency",
                      "Wave Length")


class ResultTreeModel(QtCore.QAbstractItemModel):
    '''
	a model to display a few names, ordered by sex
	'''
    def __init__(self, parent=None, result=None):
        super(ResultTreeModel, self).__init__(parent)
        self.result = result

        if result != None:
            self.setupModelData(result)

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if type(item) == type(TreeItem(None, None, None, None)):
                return item.data(index.column())
            elif type(item) == type(ChildItem(None, None, None, None)):
                return item.data(3)

        if role == QtCore.Qt.UserRole:
            if item:
                return item.person

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal
                and role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()

    def setupModelData(self, results):

        self.results = results
        self.rootItem = TreeItem("results", self.results, "results", None)

        for waveResults in results:
            itemName = "%4.2f knots" % waveResults[0].speed
            #item = self.addParent(parent, column, itemName, waveResults[0].speed)
            #person = person_class(itemName,'hej',0)
            item = TreeItem(itemName, waveResults, '', self.rootItem)

            for result in waveResults:
                itemName = "Wave dir:%4.0f deg" % result.waveAngle

                item2 = TreeItem(itemName, result, '', item)

                variables = vars(result)
                pickVariables = [
                    'addedResistance', 'verticalPlaneResponses',
                    'lateralPlaneResponses', 'pointAccelerations'
                ]

                for variable in pickVariables:
                    item3 = TreeItem(variable, variables[variable], '', item2)

                    subVariables = vars(variables[variable])

                    for subVariable in subVariables.keys():
                        if type(subVariables[subVariable]) == type(np.array([]))\
                         and subVariable !="encounterFrequencies" and subVariable !="frequencies" and subVariable !="waveLengths":

                            item4 = TreeItem(subVariable, variables[variable],
                                             '', item3)

                            item5 = ChildItem(' ', variables[variable], '',
                                              item4)
                            item4.appendChild(item5)

                            item3.appendChild(item4)

                    item2.appendChild(item3)

                item.appendChild(item2)

            self.rootItem.appendChild(item)

        a = 1


class TreeItem(object):
    '''
	a python object used to return row/column data, and keep note of
	it's parents and/or children
	'''
    def __init__(self, text, dataContainer, header, parentItem):
        self.text = text
        self.dataContainer = dataContainer
        self.parentItem = parentItem
        self.header = header
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 2

    def data(self, column):
        if self.dataContainer == None:
            if column == 0:
                return QtCore.QVariant(self.header)
            if column == 1:
                return QtCore.QVariant("")
        else:
            if column == 0:
                return QtCore.QVariant(self.text)
            if column == 1:
                return QtCore.QVariant('')
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0


class ChildItem(TreeItem):
    def __init__(self, text, dataContainer, header, parentItem):
        super(ChildItem, self).__init__(text, dataContainer, header,
                                        parentItem)

    def columnCount(self):
        return 5

    def data(self, column):
        if self.dataContainer == None:
            if column == 0:
                return QtCore.QVariant(self.header)
            if column == 1:
                return QtCore.QVariant("")
        else:
            if column == 0:
                return QtCore.QVariant(self.text)
            if column == 1:
                return QtCore.QVariant(str(self.dataContainer.waveLengths[0]))
            if column == 2:
                return QtCore.QVariant(str(self.dataContainer.waveLengths[0]))
            if column == 3:
                return QtCore.QVariant(str('nej'))
            if column == 4:
                return QtCore.QVariant(str(self.dataContainer.waveLengths[0]))

        return QtCore.QVariant()
