import sys
import os
import shutil
import subprocess
from . import scorseFileParser
from . import constants
from . import RAO
import re

class scores2CalculationClass ():

	def __init__(self,indataPath,outDataDirectory):
						
		head,tail = os.path.split(indataPath)
		
		self.indataPath = indataPath
		self.indataDirectory = head
		self.indataFileName = os.path.splitext(tail)[0] 

		self.outDataDirectory = outDataDirectory

		self.standardIndataFile = "scores.in"
		self.standardOutdataFile = "SCORES.OUT"
		self.standardCoeffFile = "COEFF.OUT"
		
		self.outDataPath = os.path.join(self.outDataDirectory,self.indataFileName + ".out")

		self.coeffPath = os.path.join(self.outDataDirectory,self.indataFileName + "-COEFF.out")

		self.errorDescriptions = {}
		self.errorDescriptions["unknown"] = r'Unknown error'
		self.errorDescriptions["  0"] = r'Too many sections, wave lengths, wave angles, etc.'
		self.errorDescriptions["  1"] = r'Sum of weight distribution does not equal the displacement'
		self.errorDescriptions["  2"] = r'The calculated displacement differs from the given nominal displacement (max 2% deviation alowed)'
		self.errorDescriptions["  3"] = r'The calculated longitudinal centre of bouyancy differ from the nomonal value ((LCB-LCG)/L max 0.5%)'
		self.errorDescriptions["  4"] = r'Error in range or increment of variable conditions'
		self.errorDescriptions["  5"] = r'TDP calculation incomplete'
		self.errorDescriptions["  6"] = r'TDP file label does not equal title data, col. 1-30'
		

	def runScores2(self):

		#Remove old indata and result files:
		if os.path.exists(self.standardIndataFile):
			os.remove(self.standardIndataFile)
		
		if os.path.exists(self.standardOutdataFile):
			os.remove(self.standardOutdataFile)

		if os.path.exists(self.standardCoeffFile):
			os.remove(self.standardCoeffFile)

		#Copy and rename indatafile:
		try : shutil.copyfile(self.indataPath,self.standardIndataFile)
		except:
			raise

		#run Scores2:
		print("Running Scores2 for %s" % self.indataFileName)
	#	os.system('scores2.exe ' + self.standardIndataFile)
		
		process = subprocess.Popen('scores2.exe',stderr=subprocess.PIPE)
		process.wait()
		

		#Copy the resultfiles to the outDataDirectory:
		try : shutil.copyfile(self.standardOutdataFile,self.outDataPath)
		except:
			raise

		try : shutil.copyfile(self.standardCoeffFile,self.coeffPath)
		except:
			raise

	def getResult(self):

		self.scoresFile = scorseFileParser.scorseFileClass(self.outDataPath)

		#Apply high wave frequency correction on the added resistance according to Bystrom:
		self.bystromCorrection()

		self.addedResistanceRAOs = self.scoresFile.getAddedResistanceRAOs(constants.rho,self.scoresFile.geometry.B,self.scoresFile.geometry.Lpp)

	def bystromCorrection(self):

		#Apply bystrom correction to all results:
		for results in self.scoresFile.results:
			for result in results:
				result.addedResistance.bystromCorrection(constants.rho,self.scoresFile.geometry.B,self.scoresFile.geometry.Lpp)
	
	def calculateAddedResistanceInIrregularWaves(self,Tz):
		
		addedResistanceRAO = self.addedResistanceRAOs[12.0][180.0]
		irregularSea = RAO.irregularSeaClass(addedResistanceRAO,constants.rho,self.scoresFile.geometry.B,self.scoresFile.geometry.Lpp,Tz)
		
		self.addedResistance = irregularSea.addedResistance	

		return irregularSea.addedResistance				

	def parseError(self):
		
		with open(self.standardOutdataFile,'r') as file:
			s = file.read()

		result = re.search("ERROR NO.(.*)",s)
		if result:
			errorCode = result.group(1)
		else:
			errorCode = 'unknown'

		if errorCode in self.errorDescriptions:
			errorDescription = self.errorDescriptions[errorCode]
		else:
			errorDescription = 'unknown error'

		if errorCode == "  2":
			calculatedDisplacement = self.parseCalculatedDisplacement()			
			if calculatedDisplacement != None:
				errorDescription += " Calculated displacement = %f m3" % calculatedDisplacement
		
		if errorCode == "  3":
			calculatedLCB = self.parseCalculatedLCB()			
			if calculatedLCB != None:
				errorDescription += " Calculated LCB = %f m (FWD. OF MIDSHIPS)" % calculatedLCB
				
		GM = self.parseGM()
		if GM != None:
			if GM < 0:
				errorDescription += " GM is negative"

		return errorCode, errorDescription

	def parseCalculatedDisplacement(self):
		
		with open(self.standardOutdataFile,'r') as file:
			s = file.read()

		result = re.search("DISPL.\(VOL.\) =(.*)",s)

		if result:
			displacement = float(result.group(1))
		else:
			displacement = None

		return displacement

	def parseCalculatedLCB(self):
		
		with open(self.standardOutdataFile,'r') as file:
			s = file.read()

		result = re.search("LONG. C.B. =([^\(]*)",s)

		if result:
			LCB = float(result.group(1))
		else:
			LCB = None

		return LCB



	def parseGM(self):
		
		with open(self.standardOutdataFile,'r') as file:
			s = file.read()

		result = re.search("GM =(.*)",s)

		if result:
			GM = float(result.group(1))
		else:
			GM = None

		return GM



def batchRunScores2(indataDirectory,outDataDirectory):

	if not os.path.exists(outDataDirectory):
		print("Create: %s" % outDataDirectory) 
		os.mkdir(outDataDirectory)
		
	indataFiles = os.listdir(indataDirectory)

	scores2Calculations = []
	for indataFile in indataFiles:
		fileName, fileExtension = os.path.splitext(indataFile)
		
		if fileExtension == ".in":
			calculation = scores2CalculationClass(os.path.join(indataDirectory,indataFile),outDataDirectory)
			calculation.runScores2()			
			calculation.getResult()		
			
			Tz = 10.0
			addedResistance = calculation.calculateAddedResistanceInIrregularWaves(Tz)			

			scores2Calculations.append(calculation)
	a=1
			


# If run interactively
if __name__ == "__main__":

	if len(sys.argv) == 3:
	
		inDataDirectory = sys.argv[1]
		outDataDirectory = sys.argv[2]
		
		
		if not os.path.exists(inDataDirectory):
			print('Error: The indataDirectory does not exist.')
			sys.exit(1)
	
		batchRunScores2(inDataDirectory,outDataDirectory)
		a=1
	else:
		print('Error: This program should be called like this: batchRunScores "inDataDirectory" "outDataDirectory')
		
		sys.exit(1)
