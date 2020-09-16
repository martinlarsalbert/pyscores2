import re

import numpy as np
import pandas as pd

from pyscores2.constants import g


class Result():
    def __init__(self, str, itemSeparator):
        self.str = str
        self.itemSeparator = itemSeparator
        self.parseString()

    def parseString(self):

        searchResult = re.search("NATURAL ROLL FREQUENCY =([^\r,^\n]*)",
                                 self.str)
        if searchResult != None:
            self.natural_roll_frequency = float(searchResult.group(1))
        else:
            self.natural_roll_frequency = None

        searchResult = re.search(
            "CALCULATED WAVE DAMPING IN ROLL =([^\r,^\n]*)", self.str)
        if searchResult != None:
            self.calculated_wave_damping_in_roll = float(searchResult.group(1))
        else:
            self.calculated_wave_damping_in_roll = None

        searchResult = re.search(
            "CRITICAL VALUE FOR DAMPING IN ROLL =([^\r,^\n]*)", self.str)
        if searchResult != None:
            self.critical_wave_damping_in_roll = float(searchResult.group(1))
        else:
            self.critical_wave_damping_in_roll = None

        searchResult = re.search("ROLL DAMPING RATIO([^\r,^\n]*)", self.str)
        if searchResult != None:
            self.roll_damping_ratio = float(searchResult.group(1))
        else:
            self.roll_damping_ratio = None

        searchResult = re.search("SPEED =([^W]*)", self.str)
        if searchResult != None:
            self.speed = float(searchResult.group(1)) * 3.6 / 1.852
            #Round the speed to nearest knot (A bit dirty way to get the Scores RAOs to collide with RAOs from file)
            self.speed = np.round(self.speed)
        else:
            self.speed = None

        searchResult = re.search("WAVE ANGLE =([^D]*)", self.str)
        self.waveAngleScores = float(searchResult.group(1))

        #ScoresII uses wave angles that go the other way 90 deg is Stbd etc. The GUI expresses the results in MDL wave angles where 90 deg is port:
        #self.waveAngle = 360 - self.waveAngleScores
        self.waveAngle = self.waveAngleScores

        self.verticalPlaneResponses = verticalPlaneResponsesClass(
            self.str, self.itemSeparator)
        self.addedResistance = addedResistanceClass(self.str,
                                                    self.itemSeparator)
        self.lateralPlaneResponses = lateralPlaneResponsesClass(
            self.str, self.itemSeparator)
        self.pointAccelerations = pointAccelerationsClass(
            self.str, self.itemSeparator)

        a = 1

    def get_result(self):
        """
		:return: pandas dataframe with results for this speed and wave direction
		"""
        responses = [
            self.verticalPlaneResponses,
            self.addedResistance,
            self.lateralPlaneResponses,
            #self.pointAccelerations,
        ]

        dfs = []
        for response in responses:

            if response.frequencies is None:
                continue

            df_ = pd.DataFrame(data=response.__dict__)
            df_.set_index(
                ['frequencies', 'encounterFrequencies', 'waveLengths'],
                inplace=True)
            df_.drop(columns=['str', 'itemSeparator'], inplace=True)
            dfs.append(df_)

        df = pd.concat(dfs, axis=1)
        df.reset_index(inplace=True)
        return df


class IrregularResults():
    def __init__(self, str, itemSeparator):
        self.str = str
        self.itemSeparator = itemSeparator
        self.results = [
        ]  #A list containing irregular results for various sea states

        if not self.isEmpty():
            self.isEmpty = False
            self.parseIrregularResults()

    def isEmpty(self):

        searchResult = re.search("RESPONSE \(AMPLITUDE\) SPECTRA", self.str)

        if searchResult:
            return False
        else:
            return True

    def parseIrregularResults(self):

        parts = re.split("RESPONSE \(AMPLITUDE\) SPECTRA", self.str)

        for part in parts[1:]:
            self.results.append(IrregularResult(part, self.itemSeparator))

        a = 1


class IrregularResult():
    """This class holds and retrieves irregular sea results if any"""
    def __init__(self, str, itemSeparator):
        self.str = str
        self.itemSeparator = itemSeparator

        self.parseAddedResistance()

    def parseAddedResistance(self):

        searchResult = re.search("AVERAGE RESIST FORCE(.*)", self.str)

        if searchResult:
            addedResistance = float(searchResult.group(1))
        else:
            raise ValueError('Added resistance could not be found')

        self.addedResistance = addedResistance


class verticalPlaneResponsesClass():
    def __init__(self, str, itemSeparator):
        self.itemSeparator = itemSeparator
        self.str = str

        self.parseString()

    def parseString(self):

        searchResult = re.search("(.*?)%s" % self.itemSeparator, self.str,
                                 re.DOTALL)
        lines = searchResult.group(1).split('\n')

        frequencies = []
        encounterFrequencies = []
        waveLengths = []
        heaveAmplitude = []
        heavePhase = []
        pitchAmplitude = []
        pitchPhase = []
        surgeAmplitude = []
        surgePhase = []

        for line in lines[6:-1]:
            values = re.split(" *", line)

            if len(values) == 11:
                #Sometimes SCores return values with cluttered columns in that case this row is not used at all...
                frequencies.append(float(values[1]))
                encounterFrequencies.append(float(values[2]))
                waveLengths.append(float(values[3]))
                heaveAmplitude.append(float(values[5]))
                heavePhase.append(float(values[6]))
                pitchAmplitude.append(float(values[7]))
                pitchPhase.append(float(values[8]))
                surgeAmplitude.append(float(values[9]))
                surgePhase.append(float(values[10]))

        self.frequencies = np.array(frequencies)
        self.encounterFrequencies = np.array(encounterFrequencies)
        self.waveLengths = np.array(waveLengths)
        self.heaveAmplitude = np.array(heaveAmplitude)
        self.heavePhase = np.array(heavePhase)
        self.pitchAmplitude = np.array(pitchAmplitude)
        self.pitchPhase = np.array(pitchPhase)
        self.surgeAmplitude = np.array(surgeAmplitude)
        self.surgePhase = np.array(surgePhase)


class addedResistanceClass():
    def __init__(self, str, itemSeparator):
        self.itemSeparator = itemSeparator
        self.str = str

        self.parseString()

        #Apply Lennart Bystroms high wave frequency added resistance correction:

    def parseString(self):

        searchResult = re.search(
            "ADDED RESISTANCE AND MOMENT(.*?)%s" % self.itemSeparator,
            self.str, re.DOTALL)
        if searchResult:
            lines = searchResult.group(1).split('\n')
        else:
            return

        frequencies = []
        encounterFrequencies = []
        waveLengths = []
        forces = []
        moments = []

        for line in lines[6:-1]:
            values = re.split(" *", line)

            if len(values) == 7:
                #Sometimes SCores return values with cluttered columns in that case this row is not used at all...
                frequencies.append(float(values[1]))
                encounterFrequencies.append(float(values[2]))
                waveLengths.append(float(values[3]))
                forces.append(float(values[5]))
                moments.append(float(values[6]))

        self.frequencies = np.array(
            frequencies)  # the wave frequency is expressed in [rad/s]
        self.encounterFrequencies = np.array(encounterFrequencies)
        self.waveLengths = np.array(waveLengths)
        self.forces = np.array(
            forces) * g / 4  #(Don't know where this factor came from?)
        self.moments = np.array(moments)

    def bystromCorrection(self, rho, B, Lpp):

        #Added resistance for frequencies above the peak frequency should all have the minimum value:
        #Addres=Raw/(raa*g*B^2*H^2/L)=0.575

        x = self.frequencies
        y = self.forces
        #Assymptotic value for added resistance:
        rawPrim = 0.575 * B**2 / Lpp * rho * g / 1000

        mm, cmax = y.max(0), y.argmax(0)
        yarg = rawPrim * 1.2

        xarg = x[cmax]

        cc2 = np.logical_and((y < rawPrim), (x > xarg))

        y[cc2] = rawPrim

        self.forcesCorrected = y


class lateralPlaneResponsesClass():
    def __init__(self, str, itemSeparator):
        self.str = str
        self.itemSeparator = itemSeparator
        self.parseString()

    def parseString(self):

        searchResult = re.search(
            "LATERAL PLANE RESPONSES(.*?)%s" % self.itemSeparator, self.str,
            re.DOTALL)

        if searchResult != None:

            lines = searchResult.group(1).split('\n')

            frequencies = []
            encounterFrequencies = []
            waveLengths = []
            swayAmplitude = []
            swayPhase = []
            yawAmplitude = []
            yawPhase = []
            rollAmplitude = []
            rollPhase = []

            for line in lines[6:-1]:
                values = re.split(" *", line)

                if len(values) == 11:
                    #Sometimes SCores return values with cluttered columns in that case this row is not used at all...
                    frequencies.append(float(values[1]))
                    encounterFrequencies.append(float(values[2]))
                    waveLengths.append(float(values[3]))
                    swayAmplitude.append(float(values[5]))
                    swayPhase.append(float(values[6]))
                    yawAmplitude.append(float(values[7]))
                    yawPhase.append(float(values[8]))
                    rollAmplitude.append(float(values[9]))
                    rollPhase.append(float(values[10]))

            self.frequencies = np.array(frequencies)
            self.encounterFrequencies = np.array(encounterFrequencies)
            self.waveLengths = np.array(waveLengths)
            self.swayAmplitude = np.array(swayAmplitude)
            self.swayPhase = np.array(swayPhase)
            self.yawAmplitude = np.array(yawAmplitude)
            self.yawPhase = np.array(yawPhase)
            self.rollAmplitude = np.array(rollAmplitude)
            self.rollPhase = np.array(rollPhase)

        else:
            self.frequencies = None
            self.encounterFrequencies = None
            self.waveLengths = None
            self.swayAmplitude = None
            self.swayPhase = None
            self.yawAmplitude = None
            self.yawPhase = None
            self.rollAmplitude = None
            self.rollPhase = None


class pointAccelerationsClass():
    def __init__(self, str, itemSeparator):
        self.itemSeparator = itemSeparator
        self.str = str
        self.parseString()

    def parseString(self):

        searchResult = re.search(
            "POINT ACCELERATIONS(.*?)SPEED", self.str, re.DOTALL
        )  #This is a bit dirty and means that only the first acceleration points is read...
        if searchResult:
            lines = searchResult.group(1).split('\n')
        else:
            return

        frequencies = []
        encounterFrequencies = []
        waveLengths = []
        verticalAmplitude = []
        verticalPhase = []
        longitudinalAmplitude = []
        longitudinalPhase = []
        lateralAmplitude = []
        lateralPhase = []

        for line in lines[10:-1]:
            values = re.split(" *", line)

            if len(values) == 11:
                #Sometimes SCores return values with cluttered columns in that case this row is not used at all...
                frequencies.append(float(values[1]))
                encounterFrequencies.append(float(values[2]))
                waveLengths.append(float(values[3]))
                verticalAmplitude.append(float(values[5]))
                verticalPhase.append(float(values[6]))
                longitudinalAmplitude.append(float(values[7]))
                longitudinalPhase.append(float(values[8]))
                lateralAmplitude.append(float(values[9]))
                lateralPhase.append(float(values[10]))

        self.frequencies = np.array(frequencies)
        self.encounterFrequencies = np.array(encounterFrequencies)
        self.waveLengths = np.array(waveLengths)
        self.verticalAmplitude = np.array(verticalAmplitude)
        self.verticalPhase = np.array(verticalPhase)
        self.longitudinalAmplitude = np.array(longitudinalAmplitude)
        self.longitudinalPhase = np.array(longitudinalPhase)
        self.lateralAmplitude = np.array(lateralAmplitude)
        self.lateralPhase = np.array(lateralPhase)
