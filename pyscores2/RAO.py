import numpy as np
import matplotlib.pyplot as plt
import logging
from scipy.interpolate import interp1d
from scipy.integrate import trapz

from .constants import g

log = logging.getLogger("RAO")


class RAOs():
    def __init__(self):
        self.RAOs = {}

    def append(self, rowIndex, columnIndex, rAO):

        #this function only appends RAOs if there are not already RAOs defined.
        #Keep in mind that points close to each other will be added:
        #RAOs[speed=10][waveDirection=180],RAOs[speed=10][waveDirection=179]
        #and will therefore both be included in the interpolations...

        newRao = True

        if rowIndex in self.RAOs:
            row = self.RAOs[rowIndex]
            if columnIndex in row:
                #If this cell already exist, nothing happends:
                newRao = False
            else:
                self.RAOs[rowIndex][columnIndex] = rAO
        else:
            self.RAOs[rowIndex] = {}
            self.RAOs[rowIndex][columnIndex] = rAO

        if newRao:
            message = "RAO ship speed:%f waveDirection:%f has been added to the ship" % (
                rowIndex, columnIndex)
        else:
            message = "RAO shipSpeed:%f waveDirection:%f has NOT been added to the ship, since the place was already taken" % (
                rowIndex, columnIndex)
        log.info(message)

        a = 1

    def get(self, rowIndex, columnIndex):
        if rowIndex in self.RAOs:
            row = self.RAOs[rowIndex]
            if columnIndex in row:
                return self.RAOs[rowIndex][columnIndex]

        raise ValueError(
            "RAO for rowIndex = %f and columnIndex = %f does not exist" %
            (rowIndex, columnIndex))

    def checkOk(self):
        #Allowed:
        #RAOs[10][180,150,120]
        #RAOs[20][180,150,120]
        #Not allowed:
        #RAOs[10][180,150,120]
        #RAOs[20][180, 160 ,120]

        speedKeys = iter(self.RAOs.values()).next().keys()

        for speeds in self.RAOs.values():
            if list(speeds.keys()) != speedKeys:
                return False

        return True


class RAO():
    def __init__(self,
                 shipSpeed,
                 waveDirection,
                 frequencies=None,
                 responses=None):
        log.info('RAO created')

        self.shipSpeed = shipSpeed
        self.waveDirection = waveDirection

        if type(frequencies) == type(np.array([])):

            self.frequencies = frequencies  #[rad/s]
            self.responses = responses

        elif frequencies == None:
            self.frequencies = np.array([])  #[rad/s]
            self.responses = np.array([])
        else:
            self.frequencies = np.array([frequencies])  #[rad/s]
            self.responses = np.array([responses])

    def append(self, frequency, response):
        self.frequencies = np.append(self.frequencies, frequency)
        self.responses = np.append(self.responses, response)

    def calculateAddedResistanceInIrregularWaves(self, rho, B, Lpp, Tzs):

        self.addedResistanceIrregularWaves = []

        for Tz in Tzs:
            self.addedResistanceIrregularWaves.append(
                irregularSeaClass(self, rho, B, Lpp, Tz))

    def calculateAddedResistanceInRegularWaves(self, rho, B, Lpp, Tps):

        #This code is used to calculated added swell (which is a simple sinus wave)

        self.addedResistanceRegularWaves = []

        for Tp in Tps:
            self.addedResistanceRegularWaves.append(
                regularSeaClass(self, rho, B, Lpp, Tp))


class irregularSeaClass():
    def __init__(self, RAO, rho, B, Lpp, Tz):

        self.Tz = Tz
        self.RAO = RAO

        self.calculateAddedResistance(rho, B, Lpp, Tz)

    def calculateAddedResistance(self, rho, B, Lpp, Tz):
        #(Matlab code originally written by Martin Kjellberg)

        Hs = 1

        maxFrequency = 20

        RAOnonDim = np.array(self.RAO.responses)
        omega = np.array(self.RAO.frequencies)

        index = omega.argsort()
        omega = omega[index]
        RAOnonDim = RAOnonDim[index]

        omegaExtended = np.append(omega, maxFrequency)
        RAOnonDimExtended = np.append(RAOnonDim, RAOnonDim[-1])

        #Refine and extend abscissa
        omegaExt = np.linspace(omegaExtended.min(), maxFrequency, 19991)

        f = interp1d(omegaExtended, RAOnonDimExtended, kind='linear')

        RAOnonDimExt = f(omegaExt)

        #Trim negative RAO values:
        RAOnonDimExt[RAOnonDimExt < 0] = 0

        # SSPA ITTC wave spectrum
        AA = 0.25 * Hs**2
        BB = (0.752 * 2 * np.pi / Tz)**4
        S = (AA * BB) * (omegaExt**(-5)) * np.exp(-BB * omegaExt**(-4))

        #Compute average added resistance by integrating over "all" frequencies
        # (Strom-Tejsen et al., Added Resistance in Waves, SNAME 1973)
        Rtmp = RAOnonDimExt * (4 * rho * g * B**2 / Lpp)  # Raw/(wave ampl ^ 2)
        Raw = 2 * trapz(Rtmp * S, x=omegaExt)

        self.addedResistance = Raw

        a = 1

        return self.addedResistance


        #plt.plot(omegaExt,S,omegaExt,RAOnonDimExt,omegaExt,(Rtmp*S)/(np.max(Rtmp*S)),omega,RAOnonDim)
        #plt.xlim(0, 4)
        #plt.show()
class regularSeaClass():
    def __init__(self, RAO, rho, B, Lpp, Tp):

        self.Tp = Tp
        self.RAO = RAO

        self.calculateAddedResistance(rho, B, Lpp, Tp)

    def calculateAddedResistance(self, rho, B, Lpp, Tp):
        #This code extracts one single wave component from the RAO

        Hs = 1

        maxFrequency = 20

        #Omega for this wave:
        omegaW = 2 * np.pi / Tp

        RAOnonDim = np.array(self.RAO.responses)
        omega = np.array(self.RAO.frequencies)

        index = omega.argsort()
        omega = omega[index]
        RAOnonDim = RAOnonDim[index]

        omegaExtended = np.append(omega, maxFrequency)
        RAOnonDimExtended = np.append(RAOnonDim, RAOnonDim[-1])

        #Refine and extend abscissa
        omegaExt = np.linspace(omegaExtended.min(), maxFrequency, 19991)

        f = interp1d(omegaExtended, RAOnonDimExtended, kind='linear')

        RAOnonDimExt = f(omegaExt)

        #Trim negative RAO values:
        RAOnonDimExt[RAOnonDimExt < 0] = 0

        #Compute added resistance for one regular wave component:
        # Raw / H^2:
        RawTmp = RAOnonDimExt * (4 * rho * g * B**2 / Lpp
                                 )  # Raw/(wave ampl ^ 2)

        if omegaW > omegaExt.min():
            #Extract the value for this wave:
            f = interp1d(omegaExt, RawTmp, kind='linear')
            Raw = f(omegaW)
        else:
            Raw = 0.0

        self.addedResistance = Raw

        a = 1
