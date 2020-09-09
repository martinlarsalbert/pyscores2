""" This is a module that reads data from a Scores1 result file"""

import re
import numpy as np


class Scores1Results(object):
    def __init__(self, filePath=None):

        self.filePath = filePath

        if self.filePath != None:
            self.loadFile()

    def loadFile(self, filePath=None):

        if filePath != None:
            self.filePath = filePath

        #Read the file:
        file = open(self.filePath, mode='r')
        self.string = file.read()
        file.close()

        #Item separator (this one is used to separate various items)
        self.itemSeparator = self.string.splitlines()[0]

        #Get wave spectra
        self.waveSpectras = self.getWaveSpectras()

        #Get response spectra (motions):
        self.getResponseSpectras()

        a = 1

    def getWaveSpectras(self):

        searchResult = re.search("0NUMBER OF WAVE SPECTRA=(.*?)\n",
                                 self.string, re.DOTALL)
        if searchResult != None:
            self.numberOfWaveSpectra = int(searchResult.group(1))
        else:
            self.numberOfWaveSpectra = 0
            waveSpectras = []
            return waveSpectras

        searchResult = re.search("0WAVE SPECTRAL DENSITY(.*)SIG\.(.*?)\n",
                                 self.string, re.DOTALL)

        spectraString = searchResult.group(1)
        sigString = searchResult.group(2)

        spectraLines = spectraString.split('\n')
        Ss = []
        omegas = []

        for i in range(self.numberOfWaveSpectra):
            Ss.append([])

        for line in spectraLines[7:-2]:

            omega = float(line[0:9])
            omegas.append(omega)

            #Needed to write this very dirty code because some of the columns colide and are not separated...

            for i in range(self.numberOfWaveSpectra):

                s = float(line[12 + i * 9:12 + (i + 1) * 9])
                Ss[i].append(s)

        waveSpectras = []

        for S in Ss:
            waveSpectras.append(WaveSpectra(omegas, S))

        return waveSpectras

    def getResponseSpectras(self):
        """This function parses data for each speed and wave direction """
        s = self.string

        for i in range(self.numberOfWaveSpectra):
            s = self.getResponseSpectra(s, self.itemSeparator)

    def getResponseSpectra(self, s, itemSeparator):
        """This function parses data for a specific speed and wave direction, 
		the data is sorted into a response structure in the corresponding wave spectra
		
		The total structure looks like this:

		self.waveSpectras[spectrum].responses[speed][waveDirection][nameTag]
		
		where
	    spectrum is the spectrum number 1,2,3...
		speed in knots
		waveDirection in deg
		nameTag is a string for instance "pitch", "sway" etc.

		"""

        searchResult = re.search("RESPONSE SPECTRA(.*?)%s(.*)" % itemSeparator,
                                 s, re.DOTALL)

        responseString = searchResult.group(1)

        restString = searchResult.group(2)

        lines = responseString.splitlines()

        searchResult = re.search("0SPEED=(.*?) KNOTS   WAVE ANGLE=(.*?) DEG",
                                 lines[1], re.DOTALL)

        speed = float(searchResult.group(1))
        waveDirection = float(searchResult.group(2))

        for line in lines[5:]:
            values = line.split()

            spectrum = int(values[0]) - 1

            nameTags = ["heave", "pitch", "sway", "yaw", "roll"]

            if speed not in self.waveSpectras[spectrum].responses:
                self.waveSpectras[spectrum].responses[speed] = {}

            if waveDirection not in self.waveSpectras[spectrum].responses[
                    speed]:
                self.waveSpectras[spectrum].responses[speed][
                    waveDirection] = {}

            colCount = 1
            for nameTag in nameTags:
                if colCount == 0:
                    value = int(values[colCount])
                else:
                    value = float(values[colCount])

                self.waveSpectras[spectrum].responses[speed][waveDirection][
                    nameTag] = value
                colCount += 1

        return restString


class WaveSpectra(object):
    def __init__(self, omegas, S):

        self.omegas = np.array(omegas)
        self.S = np.array(S)
        self.responses = {}
