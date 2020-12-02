import xml.etree.ElementTree as etree
from pyscores2 import indata


class Parser(object):
    def __init__(self, fileName=None):

        if not fileName == None:
            self.parseXML(fileName)

    def parseXML(self, fileName):

        self.fileName = fileName

        tree = etree.parse(self.fileName)

        root = tree.getroot()

        if root.tag == 'ScoresIndata':

            self.shipModel = root.find('HydroInput').find('ShipModel').text
            self.lpp = float(root.find('HydroInput').find('Lpp').text)
            self.waterDensity = float(
                root.find('HydroInput').find('WaterDensity').text)

            self.conditions = {}

            conditions = root.find('Conditions')

            for condition in conditions:

                name = condition.find('Name').text

                self.conditions[name] = Condition(condition, ship=self)

        else:
            raise ValueError('Not a valid XML file with hydrostatics data')

    def convertToScores2Indata(self,
                               tempIndata=indata.Indata(),
                               conditionName=None):

        if not conditionName in self.conditions:
            ValueError('condition: %s does not exist in file' % conditionName)

        self.scores2Indata = tempIndata

        condition = self.conditions[conditionName]

        #Move stuff from condition to self.scores2Indata:

        self.scores2Indata.cScores = []
        self.scores2Indata.bs = []
        self.scores2Indata.ts = []
        self.scores2Indata.zbars = []

        T = 0

        for section in condition.sections:

            Index = section.Index
            XPosition = section.XPosition
            Area = section.Area

            BeamWaterline = section.BeamWaterline
            Draught = section.Draught
            CenteroidZ = section.CentroidZ
            zbar = CenteroidZ

            squareArea = (BeamWaterline * Draught)
            if squareArea > 0:
                cScores = float(Area) / squareArea
            else:
                cScores = 1.0

            bs = BeamWaterline
            ts = Draught

            if Draught > T:
                T = Draught

            self.scores2Indata.cScores.append(cScores)
            self.scores2Indata.bs.append(bs)
            self.scores2Indata.ts.append(ts)
            self.scores2Indata.zbars.append(zbar)

            self.scores2Indata.lpp = self.lpp
            self.scores2Indata.draught = T
            self.scores2Indata.displacement = condition.Displacement
            self.scores2Indata.lcb = condition.LCB
            self.scores2Indata.projectName = "%s %s" % (self.shipModel,
                                                        condition.Name)
            #self.scores2Indata.speedMin = 0.0
            #self.scores2Indata.speedMax = 0.0
            #self.scores2Indata.speedIncrement = 0.0
            #self.scores2Indata.waveDirectionMin = 0.0
            #self.scores2Indata.waveDirectionMax = 0.0
            #self.scores2Indata.waveDirectionIncrement = 0.0
            #self.scores2Indata.waveFrequenciesMin = 0.2
            #self.scores2Indata.waveFrequenciesMax = 2.0
            #self.scores2Indata.waveFrequenciesIncrement = 0.05
            self.scores2Indata.kxx = 0.0
            self.scores2Indata.kyy = 0.0
            self.scores2Indata.rho = self.waterDensity
            self.scores2Indata.g = 9.80665
            self.scores2Indata.zcg = 0.0
            self.scores2Indata.partOfCriticalRollDamping = 0.0

        return self.scores2Indata


class Condition(object):
    def __init__(self, condition, ship:Parser):

        self.Name = condition.find('Name').text
        self.B = float(condition.find('B').text)
        self.TF = float(condition.find('TF').text)
        self.TA = float(condition.find('TA').text)
        self.Displacement = float(condition.find('Displacement').text)
        LCB_from_aft = float(condition.find('LCB').text)
        
        self.LCB = LCB_from_aft-ship.lpp/2
        self.LCBproc = float(condition.find('LCBproc').text)

        self.sections = []

        sections = condition.find('Sections')

        for section in sections:

            self.sections.append(Section(section))


class Section(object):
    def __init__(self, section):

        self.Index = int(section.find('Index').text)
        self.XPosition = float(section.find('XPosition').text)
        self.Area = Area = float(section.find('Area').text)
        self.BeamWaterline = float(section.find('BeamWaterline').text)
        self.Draught = float(section.find('Draught').text)
        self.CentroidZ = float(section.find('CentroidZ').text)
