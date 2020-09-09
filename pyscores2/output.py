import re
import sys
import os
import numpy as np
import pandas as pd
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
			irregularResults = IrregularResults(searchResult,self.itemSeparator)
						
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


	def get_results(self):
		"""
		This will return all reponses as a pandas data frame.
		:return df: pandas data frame
		"""
		pass

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

class Result():

	def __init__(self,str,itemSeparator):
		self.str = str
		self.itemSeparator = itemSeparator
		self.parseString()

	def parseString(self):
				
		searchResult = re.search("NATURAL ROLL FREQUENCY =([^\r,^\n]*)",self.str)
		if searchResult != None:
			self.natural_roll_frequency = float(searchResult.group(1))
		else:
			self.natural_roll_frequency = None
		
		
		searchResult = re.search("CALCULATED WAVE DAMPING IN ROLL =([^\r,^\n]*)",self.str)
		if searchResult != None:
			self.calculated_wave_damping_in_roll = float(searchResult.group(1))
		else:
			self.calculated_wave_damping_in_roll = None
		
		searchResult = re.search("CRITICAL VALUE FOR DAMPING IN ROLL =([^\r,^\n]*)",self.str)
		if searchResult != None:
			self.critical_wave_damping_in_roll = float(searchResult.group(1))
		else:
			self.critical_wave_damping_in_roll = None
		
		searchResult = re.search("ROLL DAMPING RATIO([^\r,^\n]*)",self.str)
		if searchResult != None:
			self.roll_damping_ratio = float(searchResult.group(1))
		else:
			self.roll_damping_ratio = None
			
		searchResult = re.search("SPEED =([^W]*)",self.str)
		if searchResult != None:
			self.speed = float(searchResult.group(1))*3.6/1.852
			#Round the speed to nearest knot (A bit dirty way to get the Scores RAOs to collide with RAOs from file)
			self.speed = np.round(self.speed)
		else:
			self.speed = None

		searchResult = re.search("WAVE ANGLE =([^D]*)",self.str)
		self.waveAngleScores = float(searchResult.group(1))
		
		#ScoresII uses wave angles that go the other way 90 deg is Stbd etc. The GUI expresses the results in MDL wave angles where 90 deg is port:
		self.waveAngle = 360 - self.waveAngleScores
		
		self.verticalPlaneResponses = verticalPlaneResponsesClass(self.str,self.itemSeparator)
		self.addedResistance = addedResistanceClass(self.str,self.itemSeparator)
		self.lateralPlaneResponses = lateralPlaneResponsesClass(self.str,self.itemSeparator)
		self.pointAccelerations = pointAccelerationsClass(self.str,self.itemSeparator)

		a=1

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

		dfs=[]
		for response in responses:
			df_ = pd.DataFrame(data=response.__dict__)
			df_.set_index(['frequencies','encounterFrequencies','waveLengths'], inplace=True)
			df_.drop(columns=['str','itemSeparator'], inplace=True)
			dfs.append(df_)
		
		df = pd.concat(dfs, axis=1)
		return df



class IrregularResults():

	def __init__(self,str,itemSeparator):
		self.str = str
		self.itemSeparator = itemSeparator		
		self.results = [] #A list containing irregular results for various sea states


		if not self.isEmpty():
			self.isEmpty = False
			self.parseIrregularResults()
			
	def isEmpty(self):
		
		searchResult = re.search("RESPONSE \(AMPLITUDE\) SPECTRA",self.str)

		if searchResult:
			return False
		else:
			return True

	def parseIrregularResults(self):

		parts = re.split("RESPONSE \(AMPLITUDE\) SPECTRA",self.str)

		for part in parts[1:]:
			self.results.append(IrregularResult(part,self.itemSeparator))

		a = 1


class IrregularResult():
	"""This class holds and retrieves irregular sea results if any"""

	def __init__(self,str,itemSeparator):
		self.str = str
		self.itemSeparator = itemSeparator		

		self.parseAddedResistance()

	def parseAddedResistance(self):

		searchResult = re.search("AVERAGE RESIST FORCE(.*)",self.str)

		if searchResult:
			addedResistance = float(searchResult.group(1))
		else:
			raise ValueError('Added resistance could not be found')

		self.addedResistance = addedResistance


	
class verticalPlaneResponsesClass():

	def __init__(self,str,itemSeparator):
		self.itemSeparator = itemSeparator
		self.str = str

		self.parseString()

	def parseString(self):
					
		searchResult = re.search("(.*?)%s" % self.itemSeparator,self.str,re.DOTALL)
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
			values = re.split(" *",line)
			
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
					
		self.frequencies			= 	np.array(frequencies)
		self.encounterFrequencies	= 	np.array(encounterFrequencies)
		self.waveLengths			= 	np.array(waveLengths)
		self.heaveAmplitude			= 	np.array(heaveAmplitude)
		self.heavePhase				= 	np.array(heavePhase)
		self.pitchAmplitude			= 	np.array(pitchAmplitude)
		self.pitchPhase				= 	np.array(pitchPhase)
		self.surgeAmplitude			= 	np.array(surgeAmplitude)
		self.surgePhase				= 	np.array(surgePhase)

class addedResistanceClass():

	def __init__(self,str,itemSeparator):
		self.itemSeparator = itemSeparator
		self.str = str

		self.parseString()

		#Apply Lennart Bystroms high wave frequency added resistance correction:


	def parseString(self):
						
		searchResult = re.search("ADDED RESISTANCE AND MOMENT(.*?)%s" % self.itemSeparator,self.str,re.DOTALL)
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
			values = re.split(" *",line)
			
			if len(values) == 7:
				#Sometimes SCores return values with cluttered columns in that case this row is not used at all...
				frequencies.append(float(values[1]))
				encounterFrequencies.append(float(values[2]))
				waveLengths.append(float(values[3]))
				forces.append(float(values[5]))
				moments.append(float(values[6]))
					
		self.frequencies			= 	np.array(frequencies)			# the wave frequency is expressed in [rad/s]
		self.encounterFrequencies	= 	np.array(encounterFrequencies)
		self.waveLengths			= 	np.array(waveLengths)
		self.forces					= 	np.array(forces)*g/4 #(Don't know where this factor came from?)
		self.moments				= 	np.array(moments)

	def bystromCorrection(self,rho,B,Lpp):
				
		#Added resistance for frequencies above the peak frequency should all have the minimum value:
		#Addres=Raw/(raa*g*B^2*H^2/L)=0.575
				
		x = self.frequencies
		y = self.forces
		#Assymptotic value for added resistance:
		rawPrim=0.575*B**2/Lpp*rho*g/1000;

		mm, cmax = y.max(0),y.argmax(0)
		yarg=rawPrim*1.2

		xarg=x[cmax]

		cc2=np.logical_and((y < rawPrim),(x > xarg)) 
		
		y[cc2] = rawPrim

		self.forcesCorrected = y	
		


class lateralPlaneResponsesClass():

	def __init__(self,str,itemSeparator):
		self.str = str
		self.itemSeparator = itemSeparator
		self.parseString()

	def parseString(self):		
				
		searchResult = re.search("LATERAL PLANE RESPONSES(.*?)%s" % self.itemSeparator,self.str,re.DOTALL)
		
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
				values = re.split(" *",line)
				
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
						
			self.frequencies			= 	np.array(frequencies)
			self.encounterFrequencies	= 	np.array(encounterFrequencies)
			self.waveLengths			= 	np.array(waveLengths)
			self.swayAmplitude			= 	np.array(swayAmplitude)
			self.swayPhase				= 	np.array(swayPhase)
			self.yawAmplitude			= 	np.array(yawAmplitude)
			self.yawPhase				= 	np.array(yawPhase)
			self.rollAmplitude			= 	np.array(rollAmplitude)
			self.rollPhase				= 	np.array(rollPhase)	

		else:
			self.frequencies			= None
			self.encounterFrequencies	= None
			self.waveLengths			= None
			self.swayAmplitude			= None
			self.swayPhase				= None
			self.yawAmplitude			= None
			self.yawPhase				= None
			self.rollAmplitude			= None
			self.rollPhase				= None

class pointAccelerationsClass():

	def __init__(self,str,itemSeparator):
		self.itemSeparator = itemSeparator
		self.str = str
		self.parseString()

	def parseString(self):
					
		searchResult = re.search("POINT ACCELERATIONS(.*?)SPEED",self.str,re.DOTALL) #This is a bit dirty and means that only the first acceleration points is read...
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
			values = re.split(" *",line)
			
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
					
		self.frequencies			= 	np.array(frequencies)
		self.encounterFrequencies	= 	np.array(encounterFrequencies)
		self.waveLengths			= 	np.array(waveLengths)
		self.verticalAmplitude			= 	np.array(verticalAmplitude)
		self.verticalPhase				= 	np.array(verticalPhase)
		self.longitudinalAmplitude			= 	np.array(longitudinalAmplitude)
		self.longitudinalPhase				= 	np.array(longitudinalPhase)
		self.lateralAmplitude			= 	np.array(lateralAmplitude)
		self.lateralPhase				= 	np.array(lateralPhase)

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


