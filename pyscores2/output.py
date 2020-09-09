import re
import sys
import os
import numpy as np
import pandas as pd

from pyscores2.result import Result, IrregularResults
from .constants import g
from .constants import rho
from . import waveSpectrum

from . import RAO

class OutputFile():

	def __init__(self,filePath):

		self.filePath = filePath
		self.results = {}
		self.irregularResults = {}
		
		self.loadFile()
		
		self.spectrumOrder = []
		
	def loadFile(self):
		
		with open(self.filePath,mode='r') as file:
			str = file.read()

		#This one can be used to find when certain parts of data ends.
		self.itemSeparator = str.split('\n')[0]
		
		#Add an item separator in the end of the file...
		str += self.itemSeparator

		self.string = str
		
		str1 = str
		
		#Read some geomtry stuff from the string:		
		self.getGeometry()

		#searchResults = re.split("VERTICAL PLANE RESPONSES",str1)
		#searchResults1 = re.search("VERTICAL PLANE RESPONSES(.*?)VERTICAL PLANE RESPONSES",str1,re.DOTALL).group(1)
		
		searchResults = re.split("VERTICAL PLANE RESPONSES",str1)
		
		#searchResults = []
		#searchResults.append(searchResults1)
		#searchResults.append(searchResults2)


		for searchResult in searchResults[1:]:  			

			result = Result(searchResult, self.itemSeparator)
			irregularResults = IrregularResults(searchResult, self.itemSeparator)
						
			speed = result.speed
			angle = result.waveAngle
			
			#results
			if speed in self.results:
				if angle in self.results[speed]:
					raise ValueError("Value for speed:%f, wave angle:%f already exists in results!" % (speed,angle))
				else:
					self.results[speed][angle] = result
					
			else:
				self.results[speed] = {}
				self.results[speed][angle] = result

			

		#Parse irregular sea results, if any...
		parts = re.split('RESPONSE \(AMPLITUDE\) SPECTRA',self.string)
		
		firstSpectrumIterations = {}
		for i in range(1,len(parts)):
			part = parts[i]
			previousPart = parts[i-1]

			searchResults = re.search('SPEED =([^W]*)',previousPart)
			if searchResults:
				speed = float(searchResults.group(1))*3.6/1.852
			else:
				raise ValueError('Can not find speed')

			searchResults = re.search('WAVE ANGLE =([^D]*)',previousPart)
			if searchResults:
				waveAngleScores = float(searchResults.group(1))
			else:
				raise ValueError('Can not find wave angle')

			#ScoresII uses wave angles that go the other way 90 deg is Stbd etc. The GUI expresses the results in MDL wave angles where 90 deg is port:
			waveAngle = 360 - waveAngleScores
			
			searchResults = re.search('SIG. WAVE HT. =([^,]*)',part)
			if searchResults:
				waveHeight = float(searchResults.group(1))
			else:
				raise ValueError('Can not find wave height')

			searchResults = re.search('MEAN PERIOD =(.*)',part)
			if searchResults:
				meanPeriod = float(searchResults.group(1))
			else:
				raise ValueError('Can not find mean period')	

			searchResults = re.search('AVERAGE RESIST FORCE(.*)',part)
			if searchResults:
				
				addedResistanceTons = float(searchResults.group(1))
				dimAddedresistance = addedResistanceTons * 1000 * self.geometry.g
				
				addedResistance = waveSpectrum.IrregularResult(std=None,mean = dimAddedresistance)
			else:
				raise ValueError('Can not find added resistance')	

			motions = {}
			searchResults = re.search('R.M.S.(.*)',part)
			if searchResults:
				values = searchResults.group(1).split()
				valueTitles = ['heave','pitch','sway','yaw','roll']
			
				for value,title in zip(values,valueTitles):
					motions[title] = float(value)

			else:
				raise ValueError('Can not find rms values')	
							
			spectrumIndex = "%f,%f" % (waveHeight,meanPeriod)
			
			#irregular results
			if spectrumIndex in self.irregularResults:

				if speed in self.irregularResults[spectrumIndex]:
					
					if waveAngle in self.irregularResults[spectrumIndex][speed]:
						raise ValueError("Value for speed:%f, wave angle:%f already exists in results!" % (speed,waveAngle))
					else:
						self.irregularResults[spectrumIndex][speed][waveAngle] = {}

						self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"] = {}
						self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"]["force"] = addedResistance

						self.irregularResults[spectrumIndex][speed][waveAngle]["motions"] = {}
						for title,value in motions.items():
							self.irregularResults[spectrumIndex][speed][waveAngle]["motions"][title] = waveSpectrum.IrregularResult(std=value)
												
				else:
					self.irregularResults[spectrumIndex][speed] = {}
					self.irregularResults[spectrumIndex][speed][waveAngle] = {}
					self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"] = {}
					self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"]["force"] = addedResistance

					self.irregularResults[spectrumIndex][speed][waveAngle]["motions"] = {}
					for title,value in motions.items():
						self.irregularResults[spectrumIndex][speed][waveAngle]["motions"][title] = waveSpectrum.IrregularResult(std=value)
			else:
				self.irregularResults[spectrumIndex] = {}
				self.irregularResults[spectrumIndex][speed] = {}
				self.irregularResults[spectrumIndex][speed][waveAngle] = {}
				self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"] = {}
				self.irregularResults[spectrumIndex][speed][waveAngle]["addedResistance"]["force"] = addedResistance

				self.irregularResults[spectrumIndex][speed][waveAngle]["motions"] = {}
				for title,value in motions.items():
					self.irregularResults[spectrumIndex][speed][waveAngle]["motions"][title] = waveSpectrum.IrregularResult(std=value)


		
			if spectrumIndex not in firstSpectrumIterations:
				firstSpectrumIterations[spectrumIndex] = i

			spectrumIndexDict = {}
			for spectrumIndex,i in firstSpectrumIterations.items():
				spectrumIndexDict[i] = spectrumIndex

			#This list keeps track of the order of the spectrumIndexes (based on the order they appear in the result file)
			self.spectrumIndexList = []
			for i in sorted(spectrumIndexDict.keys()):
				self.spectrumIndexList.append(spectrumIndexDict[i])


		a=1



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
			for wave_direction, results_wave_direction in results_speed.items():
				df_ = results_wave_direction.get_result()
				df_['speed']=speed
				df_['wave direction']=wave_direction
				df=df.append(df_, ignore_index=True)

		return df

	def getGeometry(self):
		#This function reads the geometry definition matrix in the beginning av the file:
			
		self.geometry = geometryClass(self.string)

	def getAddedResistanceRAOs(self,rho,B,Lpp):

		

		#The results structure is organized in the following way: results[speedIndex][angleIndex].addedResistance

		#Building a 2d dioctionary addedResistanceRAOs[speed][waveAngle] containing RAO class instances
		addedResistanceRAOs = {}
		for speed in self.results.values():
			tempDictionary = {}
			for waveDirection in speed.values():
				speed = waveDirection.speed
				waveAngle = waveDirection.waveAngle
				
				#RAOnonDim = waveDirection.addedResistance.forcesCorrected * 1000 * (shipData.rho * g * shipData.B**2 / shipData.Lpp)
				RAOnonDim = waveDirection.addedResistance.forces * 1000 / (rho * g * B**2 / Lpp)

				addedResistanceRAO = RAO.RAO(speed,waveAngle,waveDirection.addedResistance.frequencies,RAOnonDim)
				tempDictionary[waveAngle] = addedResistanceRAO

			addedResistanceRAOs[speed] = tempDictionary
			
		return addedResistanceRAOs

	def runBystromCorrectionForAll(self):

		for speedResults in self.results:
			for waveResult in speedResults:
				waveResult.addedResistance.bystromCorrection(rho,self.geometry.B,self.geometry.Lpp)
							
class geometryClass():

	def __init__(self,str):

		self.string = str

		self.parseString()

	def parseString(self):
		
		searchResult = re.search("(LENGTH =)([^D]*)",self.string)
		self.Lpp = float(searchResult.group(2))

		searchResult = re.search("(DISPL. =)([^G]*)",self.string)
		self.Displacement = float(searchResult.group(2))
		
		searchResult = re.search("DENSITY =(.*)",self.string)
		self.rho = float(searchResult.group(1))*1000 #[kg/m3]

		searchResult = re.search("GRAVITY =(.*)",self.string)
		self.g = float(searchResult.group(1))
						
		lines = self.string.split('\n')
		
		stations = []
		beams = []
		areaCoeffs = []
		drafts = []
		zBars = []
		
		for line in lines[7:28]:
			values = re.split(" *",line)
			
			stations.append(float(values[1]))
			beams.append(float(values[2]))
			areaCoeffs.append(float(values[3]))
			drafts.append(float(values[4]))
			zBars.append(float(values[5]))
								
		self.stations				= 	np.array(stations)
		self.beams					= 	np.array(beams)
		self.areaCoeffs				= 	np.array(areaCoeffs)
		self.drafts					= 	np.array(drafts)
		self.zBars					= 	np.array(zBars)
		
		self.B = np.max(self.beams)


if __name__ == "__main__":

	if len(sys.argv) == 2:
	
		scoresFilePath = sys.argv[1]	
		
		if not os.path.exists(scoresFilePath):
			print('Error: The indataDirectory does not exist.')
			sys.exit(1)
	
		scoresFile = OutputFile(scoresFilePath)
		a=1

	else:
		print('Error: This program should be called like this: scoresFileParser "scoresFilePath"')
		
		sys.exit(1)


