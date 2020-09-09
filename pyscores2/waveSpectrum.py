import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import trapz


class WaveSpectrum(object):
    def __init__(self, name=''):
        self.name = name
        self.results = {}
        self.includeInScoresFile = True
        self.scoresFileID = None  #This is the ID number that is used in the scores file for this spectrum

    def get(self, frequencies):
        pass

    def getType(self):
        return self.__class__.__name__

    def calculateFromScoresFile(self, scoresFile):

        for speed in sorted(scoresFile.results.keys()):

            self.results[speed] = {}

            for waveAngle in sorted(scoresFile.results[speed].keys()):

                #result.addedResistance.forces
                #result.addedResistance.moments

                result = scoresFile.results[speed][waveAngle]
                self.results[speed][waveAngle] = {}

                #result.lateralPlaneResponses
                self.results[speed][waveAngle]['lateralPlaneResponses'] = {}
                if result.lateralPlaneResponses.frequencies == None:
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'sway'] = IrregularResult(0, 0, 0, 0)
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'yaw'] = IrregularResult(0, 0, 0, 0)
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'roll'] = IrregularResult(0, 0, 0, 0)
                else:
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'sway'] = self.calculateLinearResponse(
                            result.lateralPlaneResponses.frequencies,
                            result.lateralPlaneResponses.swayAmplitude)
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'yaw'] = self.calculateLinearResponse(
                            result.lateralPlaneResponses.frequencies,
                            result.lateralPlaneResponses.yawAmplitude)
                    self.results[speed][waveAngle]['lateralPlaneResponses'][
                        'roll'] = self.calculateLinearResponse(
                            result.lateralPlaneResponses.frequencies,
                            result.lateralPlaneResponses.rollAmplitude)

                #result.verticalPlaneResponses
                self.results[speed][waveAngle]['verticalPlaneResponses'] = {}
                if result.verticalPlaneResponses.frequencies == None:
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'surge'] = IrregularResult(0, 0, 0, 0)
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'heave'] = IrregularResult(0, 0, 0, 0)
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'pitch'] = IrregularResult(0, 0, 0, 0)
                else:
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'surge'] = self.calculateLinearResponse(
                            result.verticalPlaneResponses.frequencies,
                            result.verticalPlaneResponses.surgeAmplitude)
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'heave'] = self.calculateLinearResponse(
                            result.verticalPlaneResponses.frequencies,
                            result.verticalPlaneResponses.heaveAmplitude)
                    self.results[speed][waveAngle]['verticalPlaneResponses'][
                        'pitch'] = self.calculateLinearResponse(
                            result.verticalPlaneResponses.frequencies,
                            result.verticalPlaneResponses.pitchAmplitude)

                #result.pointAccelerations
                if hasattr(result.pointAccelerations, 'frequencies'):
                    self.results[speed][waveAngle]['pointAccelerations'] = {}
                    if result.pointAccelerations.frequencies == None:
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'x'] = IrregularResult(0, 0, 0, 0)
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'y'] = IrregularResult(0, 0, 0, 0)
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'z'] = IrregularResult(0, 0, 0, 0)
                    else:
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'x'] = self.calculateLinearResponse(
                                result.pointAccelerations.frequencies, result.
                                pointAccelerations.longitudinalAmplitude)
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'y'] = self.calculateLinearResponse(
                                result.pointAccelerations.frequencies,
                                result.pointAccelerations.lateralAmplitude)
                        self.results[speed][waveAngle]['pointAccelerations'][
                            'z'] = self.calculateLinearResponse(
                                result.pointAccelerations.frequencies,
                                result.pointAccelerations.verticalAmplitude)

                a = 1

        return self.results

    def calculateLinearResponse(self, RAOFrequencies, RAO):
        #Compute response in irregular waves by integrating over "all" frequencies:

        if RAO == None:
            return IrregularResult(-999, -999, RAOFrequencies, RAO)

        SPrim = self.get()
        cutIndex = np.logical_and(
            min(RAOFrequencies) <= self.frequencies,
            max(RAOFrequencies) >= self.frequencies)
        frequencies = self.frequencies[cutIndex]
        S = SPrim[cutIndex]

        try:
            f = interp1d(RAOFrequencies, RAO, kind='linear')
            RAOInterp = f(frequencies)
        except:
            a = 1

        response = RAOInterp**2 * S

        variance = trapz(response, x=frequencies)
        std = np.sqrt(variance)

        return IrregularResult(std, 0, RAOFrequencies, RAO)


class ITTCSpectrum(WaveSpectrum):
    def __init__(self, name, Hs=None, Tz=None):
        super(ITTCSpectrum, self).__init__(name)

        self.scoresFileID = 3

        if Hs != None:
            self.define(Hs, Tz)
        else:
            self.Hs = 0
            self.Tz = 0

    def define(self, Hs, Tz):
        self.Hs = Hs  #Significant wave height [m]
        self.Tz = Tz  #Zero crossing period [s]

    def get(self, frequencies=None):

        if frequencies == None:
            self.frequencies = np.linspace(0.01, 4, 1000)
        else:
            self.frequencies = np.array(frequencies)  # [rad/s]

        self.A = 0.25 * (self.Hs)**2
        self.B = (0.752 * 2 * np.pi / self.Tz)**4

        self.S = self.A * self.B * self.frequencies**(-5) * np.exp(
            -self.B * self.frequencies**(-4))

        return self.S

    def getParameterDict(self):

        parameterDict = {}
        parameterDict['Hs'] = self.Hs
        parameterDict['Tz'] = self.Tz

        return parameterDict

    def getTitle(self):
        return "%s Hs:%f Tz:%f" % (self.name, self.Hs, self.Tz)

    def getParameters(self):
        """The parameters that should be passed to the scores file"""
        parameters = [self.Hs, self.Tz]
        return parameters


class JonswapSpectrum(WaveSpectrum):
    def __init__(self, name, Hs=None, Tp=None, gamma=None):
        super(JonswapSpectrum, self).__init__(name)

        self.scoresFileID = 6

        if gamma == None:
            self.gamma = 3.3

        if Hs != None:
            self.define(Hs, Tp, gamma)
        else:
            self.Hs = 0
            self.Tp = 0

    def define(self, Hs, Tp, gamma):
        self.Hs = Hs  #Significant wave height [m]
        self.Tp = Tp  #Modal period [s]
        if gamma != None:
            self.gamma = gamma

    def get(self, frequencies=None):
        #The code to generate a Jonswap spectrum has been converted from the waveref.m from MDLUtv.

        nw = 200
        tz = self.Tp / 1.4077  #This should perhaps be 1.29 or a function of gamma...
        t1 = 1.0864 * tz
        omz = 2 * np.pi / tz
        a = 173 * self.Hs**2 / t1**4
        b = 691 / t1**4

        if frequencies == None:

            wmin = 0.4 * omz
            wmax = 3 * omz
            dw = (wmax - wmin) / (nw - 1)
            self.frequencies = np.arange(wmin, wmax, dw)

        else:
            self.frequencies = np.array(frequencies)  # [rad/s]

        s1 = a / self.frequencies**5
        s2 = np.exp(-b / self.frequencies**4)
        ss = s1 * s2

        S = []
        gam = np.array([1, 2, 3, 3.3, 4, 5, 6])
        f = np.array([1, 1.24, 1.46, 1.52, 1.66, 1.86, 2.04])
        c = np.polyfit(gam, f, 4)
        f1 = np.polyval(c, self.gamma)
        k = 1 / f1

        for frequency, s in zip(self.frequencies, ss):
            if frequency < 2 * np.pi / self.Tp:
                sigma = 0.07
            else:
                sigma = 0.09

            fct = np.exp(-1 / 2 / sigma**2 *
                         (0.159 * frequency * self.Tp - 1)**2)

            S.append(k * s * self.gamma**fct)

        self.S = np.array(S)
        return self.S

    def getParameterDict(self):

        parameterDict = {}
        parameterDict['Hs'] = self.Hs
        parameterDict['Tp'] = self.Tp

        return parameterDict

    def getTitle(self):
        return "%s Hs:%f Tp:%f" % (self.name, self.Hs, self.Tp)

    def getParameters(self):
        """The parameters that should be passed to the scores file"""
        parameters = [2 * np.pi / self.Tp, self.Hs]
        return parameters


class IrregularResult():
    def __init__(self, std=None, mean=None, RAOFrequencies=None, RAO=None):

        self.std = std
        if self.std:
            self.significantValue = 2 * self.std
        else:
            self.significantValue = None

        self.mean = mean
        self.RAOFrequencies = RAOFrequencies
        self.RAO = RAO


class FileSpectrum(WaveSpectrum):
    def __init__(self, name, frequencies, Ss, Hs=None, Tz=None):
        super(FileSpectrum, self).__init__(name)

        self.includeInScoresFile = False  #These can not be included in the Scoresfile

        self.frequencies = np.array(frequencies)
        self.S = np.array(Ss)

        if Hs != None:
            self.define(Hs, Tz)
        else:
            self.Hs = 0
            self.Tz = 0

    def define(self, Hs, Tz):
        self.Hs = Hs  #Significant wave height [m]
        self.Tz = Tz  #Zero crossing period [s]

    def get(self, frequencies=None):

        return self.S

    def getParameterDict(self):

        parameterDict = {}
        parameterDict['Hs'] = self.Hs
        parameterDict['Tz'] = self.Tz

        return parameterDict

    def getTitle(self):
        return "%s from file" % (self.name)
