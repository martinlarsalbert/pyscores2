import re
import sys
import os
import numpy as np
import pandas as pd
from scipy.integrate import simps

from pyscores2.result import Result, IrregularResults
from .constants import g
from .constants import rho
from . import waveSpectrum

from . import RAO
import pyscores2

class OutputFile():
    def __init__(self, filePath):

        self.filePath = filePath
        self.results = {}
        self.irregularResults = {}

        self.loadFile()

        self.spectrumOrder = []

    def loadFile(self):

        with open(self.filePath, mode='r') as file:
            str = file.read()

        if os.path.getsize(self.filePath) == 0:
            raise pyscores2.OutputFileEmptyError('Output file too small (%s)' % self.filePath)

        #This one can be used to find when certain parts of data ends.
        self.itemSeparator = str.split('\n')[0]

        #Add an item separator in the end of the file...
        str += self.itemSeparator

        self.string = str

        str1 = str

        #Read some geomtry stuff from the string:
        self.getGeometry()

        # Read section coefficients:
        self.get_section_coefficients()

        #searchResults = re.split("VERTICAL PLANE RESPONSES",str1)
        #searchResults1 = re.search("VERTICAL PLANE RESPONSES(.*?)VERTICAL PLANE RESPONSES",str1,re.DOTALL).group(1)

        searchResults = re.split("VERTICAL PLANE RESPONSES", str1)

        #searchResults = []
        #searchResults.append(searchResults1)
        #searchResults.append(searchResults2)

        for searchResult in searchResults[1:]:

            result = Result(searchResult, self.itemSeparator)
            irregularResults = IrregularResults(searchResult,
                                                self.itemSeparator)

            speed = result.speed
            angle = result.waveAngle

            #results
            if speed in self.results:
                if angle in self.results[speed]:
                    raise ValueError(
                        "Value for speed:%f, wave angle:%f already exists in results!"
                        % (speed, angle))
                else:
                    self.results[speed][angle] = result

            else:
                self.results[speed] = {}
                self.results[speed][angle] = result

        #Parse irregular sea results, if any...
        parts = re.split('RESPONSE \(AMPLITUDE\) SPECTRA', self.string)

        firstSpectrumIterations = {}
        for i in range(1, len(parts)):
            part = parts[i]
            previousPart = parts[i - 1]

            searchResults = re.search('SPEED =([^W]*)', previousPart)
            if searchResults:
                speed = float(searchResults.group(1)) * 3.6 / 1.852
            else:
                raise ValueError('Can not find speed')

            searchResults = re.search('WAVE ANGLE =([^D]*)', previousPart)
            if searchResults:
                waveAngleScores = float(searchResults.group(1))
            else:
                raise ValueError('Can not find wave angle')

            #ScoresII uses wave angles that go the other way 90 deg is Stbd etc. The GUI expresses the results in MDL wave angles where 90 deg is port:
            waveAngle = 360 - waveAngleScores

            searchResults = re.search('SIG. WAVE HT. =([^,]*)', part)
            if searchResults:
                waveHeight = float(searchResults.group(1))
            else:
                raise ValueError('Can not find wave height')

            searchResults = re.search('MEAN PERIOD =(.*)', part)
            if searchResults:
                meanPeriod = float(searchResults.group(1))
            else:
                raise ValueError('Can not find mean period')

            searchResults = re.search('AVERAGE RESIST FORCE(.*)', part)
            if searchResults:

                addedResistanceTons = float(searchResults.group(1))
                dimAddedresistance = addedResistanceTons * 1000 * self.geometry.g

                addedResistance = waveSpectrum.IrregularResult(
                    std=None, mean=dimAddedresistance)
            else:
                raise ValueError('Can not find added resistance')

            motions = {}
            searchResults = re.search('R.M.S.(.*)', part)
            if searchResults:
                values = searchResults.group(1).split()
                valueTitles = ['heave', 'pitch', 'sway', 'yaw', 'roll']

                for value, title in zip(values, valueTitles):
                    motions[title] = float(value)

            else:
                raise ValueError('Can not find rms values')

            spectrumIndex = "%f,%f" % (waveHeight, meanPeriod)

            #irregular results
            if spectrumIndex in self.irregularResults:

                if speed in self.irregularResults[spectrumIndex]:

                    if waveAngle in self.irregularResults[spectrumIndex][
                            speed]:
                        raise ValueError(
                            "Value for speed:%f, wave angle:%f already exists in results!"
                            % (speed, waveAngle))
                    else:
                        self.irregularResults[spectrumIndex][speed][
                            waveAngle] = {}

                        self.irregularResults[spectrumIndex][speed][waveAngle][
                            "addedResistance"] = {}
                        self.irregularResults[spectrumIndex][speed][waveAngle][
                            "addedResistance"]["force"] = addedResistance

                        self.irregularResults[spectrumIndex][speed][waveAngle][
                            "motions"] = {}
                        for title, value in motions.items():
                            self.irregularResults[spectrumIndex][speed][
                                waveAngle]["motions"][
                                    title] = waveSpectrum.IrregularResult(
                                        std=value)

                else:
                    self.irregularResults[spectrumIndex][speed] = {}
                    self.irregularResults[spectrumIndex][speed][waveAngle] = {}
                    self.irregularResults[spectrumIndex][speed][waveAngle][
                        "addedResistance"] = {}
                    self.irregularResults[spectrumIndex][speed][waveAngle][
                        "addedResistance"]["force"] = addedResistance

                    self.irregularResults[spectrumIndex][speed][waveAngle][
                        "motions"] = {}
                    for title, value in motions.items():
                        self.irregularResults[spectrumIndex][speed][waveAngle][
                            "motions"][title] = waveSpectrum.IrregularResult(
                                std=value)
            else:
                self.irregularResults[spectrumIndex] = {}
                self.irregularResults[spectrumIndex][speed] = {}
                self.irregularResults[spectrumIndex][speed][waveAngle] = {}
                self.irregularResults[spectrumIndex][speed][waveAngle][
                    "addedResistance"] = {}
                self.irregularResults[spectrumIndex][speed][waveAngle][
                    "addedResistance"]["force"] = addedResistance

                self.irregularResults[spectrumIndex][speed][waveAngle][
                    "motions"] = {}
                for title, value in motions.items():
                    self.irregularResults[spectrumIndex][speed][waveAngle][
                        "motions"][title] = waveSpectrum.IrregularResult(
                            std=value)

            if spectrumIndex not in firstSpectrumIterations:
                firstSpectrumIterations[spectrumIndex] = i

            spectrumIndexDict = {}
            for spectrumIndex, i in firstSpectrumIterations.items():
                spectrumIndexDict[i] = spectrumIndex

            #This list keeps track of the order of the spectrumIndexes (based on the order they appear in the result file)
            self.spectrumIndexList = []
            for i in sorted(spectrumIndexDict.keys()):
                self.spectrumIndexList.append(spectrumIndexDict[i])

        a = 1

        #Load spectra results (if any)
        #searchResult = re.search("RESPONSE \(AMPLITUDE\) SPECTRA(.*?)SPECTRA OF ACCELERATIONS",self.string,re.DOTALL)
        #
        #if searchResult.group(0) != None:
        #
        #	line = searchResult.group(1).split('\n')[5]
        #	if len(re.split(" *",line)) > 1:
        #		#--> Wave spectra present
        #
        #		self.resultSpectra = {}

        #"RESPONSE (AMPLITUDE) SPECTRA"

    def get_result(self):
        """
		This will return all reponses as a pandas data frame.
		:return df: pandas data frame
		"""
        df = pd.DataFrame()

        for speed, results_speed in self.results.items():
            for wave_direction, results_wave_direction in results_speed.items(
            ):
                df_ = results_wave_direction.get_result()
                df_['speed'] = speed
                df_['wave direction'] = wave_direction
                df = df.append(df_, ignore_index=True)

        return df

    def get_roll_damping(self):
        df = pd.DataFrame()

        for speed, results_speed in self.results.items():
            for wave_direction, results_wave_direction in results_speed.items():
                assert isinstance(results_wave_direction,Result)
                s = pd.Series()
                s['speed']=speed
                s['wave_direction']=wave_direction
                s['calculated_wave_damping_in_roll']=results_wave_direction.calculated_wave_damping_in_roll
                s['critical_wave_damping_in_roll'] = results_wave_direction.critical_wave_damping_in_roll
                s['natural_roll_frequency'] = results_wave_direction.natural_roll_frequency
                s['roll_damping_ratio'] = results_wave_direction.roll_damping_ratio
                df=df.append(s, ignore_index=True)

        return df

    def getGeometry(self):
        #This function reads the geometry definition matrix in the beginning av the file:

        self.geometry = geometryClass(self.string)

    def get_section_coefficients(self):
        """
        Get the section coefficients
        :return: pd.DataFrame with coefficients for all sections.
        """
        s = self.string
        parts = re.split('0          TWO-DIMENSIONAL SECTION PROPERTIES', s)
        s2 = parts[-1]

        project_name=re.search('.+',s).group(0)

        end_tags = [project_name, '0STOP']

        s3=s2
        for end_tag in end_tags:
            parts = re.split(end_tag, s3)
            s3 = parts[0]

        result = re.search('[^\n]+\n([^\n]+)', s3)
        keys = result.group(1).split()
        keys[0] = 'FREQ.'

        parts = re.split('STA.*', s3)
        df_stations = pd.DataFrame()
        for i, part in enumerate(parts[1:]):
            data_ = np.fromstring(part, sep=' ')
            assert len(data_) % len(keys) == 0
            n_rows = int(len(data_) / len(keys))
            data_2 = data_.reshape(n_rows, len(keys))
            df_data = pd.DataFrame(data=data_2, columns=keys)
            df_data['station'] = i
            df_stations = df_stations.append(df_data, ignore_index=True, sort=False)

        self.df_sections = df_stations
        return df_stations


    def calculate_B_W0(self):
        """
        Calculate the wave roll damping at zero speed (Input to the Ikeda method)
        :return: w,B_W0 (frequency [rad/s], Wave damping [Nm*s/rad])
        """
        df_stations = self.df_sections
        lpp=self.geometry.Lpp

        # Convert dataframes to matrixes for all sections:
        (n_rows, _) = df_stations.groupby(by='station').get_group(0).shape
        N_rs = np.zeros(shape=(n_rows, 21))
        N_s_phis = np.zeros(shape=(n_rows, 21))
        N_RSs = np.zeros(shape=(n_rows, 21))
        N_Ss = np.zeros(shape=(n_rows, 21))

        for station, df_station in df_stations.groupby(by='station'):
            N_rs[:, station] = df_station['N-SUB(R)']
            N_s_phis[:, station] = df_station['N(S.PHI)']
            #N_RSs[:, station] = df_station['N-SUB(R.S)']
            #N_Ss[:, station] = df_station['N-SUB(S)']

        w=df_station['FREQ.']  # [rad/s]

        # Integrate over all sections:
        N_r = np.zeros(n_rows)
        N_s_phi = np.zeros(n_rows)
        #N_RS = np.zeros(n_rows)
        #N_S = np.zeros(n_rows)

        x_21=np.linspace(0,lpp,21)
        for i in range(n_rows):
            N_r[i] = simps(y=N_rs[i, :], x=x_21)
            N_s_phi[i] = simps(y=N_s_phis[i, :], x=x_21)
            #N_RS[i] = simps(y=N_RSs[i, :], x=x_21)
            #N_S[i] = simps(y=N_Ss[i, :], x=x_21)

        draught=self.geometry.drafts.max()
        OG = self.geometry.vcg - draught
        B_W0 = N_r + OG * N_s_phi
        rho = self.geometry.rho
        B_W0*=1000  # Scores results are given i tons (I think)
        return w,B_W0

    def getAddedResistanceRAOs(self, rho, B, Lpp):

        #The results structure is organized in the following way: results[speedIndex][angleIndex].addedResistance

        #Building a 2d dioctionary addedResistanceRAOs[speed][waveAngle] containing RAO class instances
        addedResistanceRAOs = {}
        for speed in self.results.values():
            tempDictionary = {}
            for waveDirection in speed.values():
                speed = waveDirection.speed
                waveAngle = waveDirection.waveAngle

                #RAOnonDim = waveDirection.addedResistance.forcesCorrected * 1000 * (shipData.rho * g * shipData.B**2 / shipData.Lpp)
                RAOnonDim = waveDirection.addedResistance.forces * 1000 / (
                    rho * g * B**2 / Lpp)

                addedResistanceRAO = RAO.RAO(
                    speed, waveAngle,
                    waveDirection.addedResistance.frequencies, RAOnonDim)
                tempDictionary[waveAngle] = addedResistanceRAO

            addedResistanceRAOs[speed] = tempDictionary

        return addedResistanceRAOs

    def runBystromCorrectionForAll(self):

        for speedResults in self.results:
            for waveResult in speedResults:
                waveResult.addedResistance.bystromCorrection(
                    rho, self.geometry.B, self.geometry.Lpp)


class geometryClass():
    def __init__(self, str):

        self.string = str

        self.parseString()

    def parseString(self):

        searchResult = re.search("(LENGTH =)([^D]*)", self.string)
        self.Lpp = float(searchResult.group(2))

        searchResult = re.search("(DISPL. =)([^G]*)", self.string)
        self.Displacement = float(searchResult.group(2))

        searchResult = re.search("DENSITY =(.*)", self.string)
        self.rho = float(searchResult.group(1)) * 1000  #[kg/m3]

        searchResult = re.search("GRAVITY =(.*)", self.string)
        self.g = float(searchResult.group(1))

        searchResult = re.search("VCG = +(\S+)", self.string)
        self.vcg = float(searchResult.group(1))

        lines = self.string.split('\n')

        stations = []
        beams = []
        areaCoeffs = []
        drafts = []
        zBars = []

        for line in lines[7:28]:
            values = re.split(" *", line)

            stations.append(float(values[1]))
            beams.append(float(values[2]))
            areaCoeffs.append(float(values[3]))
            drafts.append(float(values[4]))
            zBars.append(float(values[5]))

        self.stations = np.array(stations)
        self.beams = np.array(beams)
        self.areaCoeffs = np.array(areaCoeffs)
        self.drafts = np.array(drafts)
        self.zBars = np.array(zBars)

        self.B = np.max(self.beams)


if __name__ == "__main__":

    if len(sys.argv) == 2:

        scoresFilePath = sys.argv[1]

        if not os.path.exists(scoresFilePath):
            print('Error: The indataDirectory does not exist.')
            sys.exit(1)

        scoresFile = OutputFile(scoresFilePath)
        a = 1

    else:
        print(
            'Error: This program should be called like this: scoresFileParser "scoresFilePath"'
        )

        sys.exit(1)
