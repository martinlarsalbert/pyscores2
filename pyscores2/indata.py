# This module can open and save indata files for ScoresII
import numpy as np
import pyscores2

class Indata():
    def __init__(self):

        self.cScores = []                       # [-]
        self.bs = []                            # [m]
        self.ts = []                            # [m]
        self.zbars = []                         # [m]
        self.lpp = 0.0                          # [m]
        self.draught = 0.0                      # [m]
        self.displacement = 0.0                 # [m3]
        self.lcb = 0.0                          # From LPP/2 [m]
        self.projectName = "New Project"
        self.speedMin = 0.0                     # [kts]
        self.speedMax = 10.0                    # [kts]
        self.speedIncrement = 5.0               # [kts]
        self.waveDirectionMin = 0.0             # [deg]
        self.waveDirectionMax = 180.0           # [deg]
        self.waveDirectionIncrement = 30.0      # [deg]
        self.waveFrequenciesMin = 0.2           # [rad/s]
        self.waveFrequenciesMax = 2.0           # [rad/s]
        self.waveFrequenciesIncrement = 0.05    # [rad/s]
        self.kxx = 0.0                          # [m]
        self.kyy = 0.0                          # [m]
        self.rho = 1025.0                       # [kg/m3]
        self.g = 9.80665                        # [m/s^2]
        self.zcg = 0.0                          # [m]
        self.partOfCriticalRollDamping = 0.0    # [-]

        self.lines = ""

        self.runOptions = {}
        # Tags in the Option control card to Scores II:
        self.runOptionTags = [
            "IA",  # 1
            "IB",  # 3
            "IC",  # 5
            "ID",  # 7
            "IE",  # 9
            "IF",  # 11
            "IG",  # 13
            "IH",  # 15
            "II",  # 17
            "IJ",  # 19
            "N",  # 21
            "IK",  # 23
            "IL",  # 25
            "IM",  # 27
            "NMOT",  # 29
            "NMOOR"
        ]  # 31

        self.runOptions["IA"] = RunOption(description=r"Hull form segments")
        self.runOptions["IA"].addOption(
            description=r"Hullform given at segment midpoint")
        self.runOptions["IA"].addOption(
            description=r"Hullform given at segment endpoint")
        self.runOptions["IA"].set_value(1)

        self.runOptions["IB"] = RunOption(description=r"Mass & Moment")
        self.runOptions["IB"].addOption(
            description=r"Motion only, use ship total mass properties")
        self.runOptions["IB"].addOption(
            description=r"Motion only, use mass dist.")
        self.runOptions["IB"].set_value(0)

        self.runOptions["IC"] = RunOption(description=r"Mass dist.")
        self.runOptions["IC"].addOption(description=r"Mass distribution")
        self.runOptions["IC"].addOption(description=r"Weight distribution")
        self.runOptions["IC"].set_value(0)

        self.runOptions["ID"] = RunOption(description=r"Wave Spectra")
        self.runOptions["ID"].addOption(description=r"Regular Waves")
        self.runOptions["ID"].addOption(description=r"Neuman Spectra")
        self.runOptions["ID"].addOption(description=r"Pierson-Moskowitz")
        self.runOptions["ID"].addOption(description=r"Two parameter")
        self.runOptions["ID"].addOption(description=r"Tabulated")
        self.runOptions["ID"].addOption(description=r"Bretschneider")
        self.runOptions["ID"].addOption(description=r"Jonswap")
        self.runOptions["ID"].set_value(0)

        self.runOptions["IE"] = RunOption(description=r"Degrees of freedom")
        self.runOptions["IE"].addOption(description=r"Vertical plane")
        self.runOptions["IE"].addOption(
            description=r"Vertical and Lateral plane")
        self.runOptions["IE"].addOption(description=r"Lateral plane only")
        self.runOptions["IE"].set_value(1)

        self.runOptions["IF"] = RunOption(description=r"Directionality")
        self.runOptions["IF"].addOption(description=r"Uni-directional waves")
        self.runOptions["IF"].addOption(
            description=r"Cos-square wave spreading")
        self.runOptions["IF"].set_value(0)

        self.runOptions["IG"] = RunOption(description=r"TDP File")
        self.runOptions["IG"].addOption(description=r"Generate TDP file")
        self.runOptions["IG"].addOption(description=r"Read TDP file")
        self.runOptions["IG"].set_value(0)

        self.runOptions["IH"] = RunOption(description=r"Moment closure")
        self.runOptions["IH"].addOption(description=r"Supress closure calc")
        self.runOptions["IH"].addOption(
            description=r"Calc. and print out closure results")
        self.runOptions["IH"].set_value(0)

        self.runOptions["II"] = RunOption(description=r"Output form")
        self.runOptions["II"].addOption(description=r"Dimensional")
        self.runOptions["II"].addOption(description=r"Non-dimensional")
        self.runOptions["II"].set_value(0)

        self.runOptions["IJ"] = RunOption(description=r"Torsion axis")
        self.runOptions["IJ"].addOption(description=r"Centre of gravity")
        self.runOptions["IJ"].addOption(description=r"Waterline")
        self.runOptions["IJ"].set_value(0)

        self.runOptions["N"] = RunOption(
            description=r"No. of equally spaced segments along the ship")
        self.runOptions["N"].set_value(20)

        self.runOptions["IK"] = RunOption(description=r"Roll damping")
        self.runOptions["IK"].addOption(
            description=r"Input empirical total damping")
        self.runOptions["IK"].addOption(
            description=r"Input empirical nonlinear damping")
        self.runOptions["IK"].addOption(
            description=r"Use program calculated nonlinear damping")
        self.runOptions["IK"].set_value(0)

        self.runOptions["IL"] = RunOption(
            description=r"Use 3-D Damping correction factors heave & pitch")
        self.runOptions["IL"].addOption(description=r"No correction")
        self.runOptions["IL"].addOption(
            description=r"Use 3-D correction factors")
        self.runOptions["IL"].set_value(0)

        self.runOptions["IM"] = RunOption(
            description=
            r"Total number of sections to be analyzed by close-fitted method")
        self.runOptions["IM"].set_value(0)

        self.runOptions["NMOT"] = RunOption(description=r"Motion output")
        self.runOptions["NMOT"].set_value(0)

        self.runOptions["NMOOR"] = RunOption(description=r"Moring option")
        self.runOptions["NMOOR"].set_value(0)

        self.accelerationPoints = []

    def open(self, indataPath):
        self.indataPath = str(indataPath)

        try:
            file = open(self.indataPath, 'r')
            lines = file.readlines()
            file.close()
        except IOError:
            print("Error: can\'t find file or read data")

        # 1  Title Card_________________________________
        self.projectName = lines[0].replace("\n", "")

        # 2  Run option Control Card____________________
        # Try to parse the run options control card according to manual page 40-
        # 1	IA		hullFormSegments
        # 2	IB		massAndMoment
        # 3	IC		massDistribution
        # 4	ID		waveSpectra
        # 5	IE		degreesOfFreedom
        # 6	IF		directionality
        # 11	NMOT	motionOutPut

        runOptionString = lines[1]

        firstIndex = 0
        for tag in self.runOptionTags:
            partString = runOptionString[firstIndex:firstIndex + 2]
            value = intSpecial(partString)
            self.runOptions[tag].set_value(value)
            firstIndex += 2

        # 3  Length Card________________________________
        values = lines[2].split()
        self.lpp = float(values[0])
        self.rho = float(values[1]) * 1000  # [kg/m3]
        self.g = float(values[2])
        self.displacement = float(values[3])

        # 4  Hull form cards____________________________
        bs = []
        cScores = []
        ts = []
        for rowCounter in range(3, len(lines)):
            line = lines[rowCounter]
            values = line.split()

            if (len(values) == 3) or (len(values) == 4):

                self.bs.append(float(values[0]))
                self.cScores.append(float(values[1]))
                self.ts.append(float(values[2]))

                if (len(values) == 3):
                    self.zbars=list(np.zeros(len(self.cScores)))
                else:
                    self.zbars.append(float(values[3]))
            else:
                break

        # The frames in ScoresII are counted from FP, but this GUI uses a traditional numbering from AP so the geomtry vectors have to be reversed.
        self.bs=np.flipud(self.bs)
        self.cScores=np.flipud(self.cScores)
        self.ts=np.flipud(self.ts)
        self.zbars=np.flipud(self.zbars)

        # 5  Section Card_______________________________
        # (Needed only if close-fitted option IM > 0
        # ...

        # 6  Section offset card_______________________
        # "These cards appear in the input only if the closefit option tag (IM) is greater than zero..."

        # 7  Lateral plane card________________________
        values = lines[rowCounter].split()
        self.zcg = float(values[0])
        self.kxx = float(values[1])

        # 8  Longitudinal total mass properties card____
        # "This card is used only if the moment option tag IB is 0..."
        rowCounter += 1
        values = lines[rowCounter].split()
        self.kyy = float(values[0])
        faktor = float(values[1])
        self.lcb = -faktor+self.lpp/2

        # 9  Sectional mass properties__________________
        # ...

        # 10 Vertical Bending Moment Station and...
        # "...needed only if the degrees of freeedom option tag (IE) is 0 or 1.
        # ...
        rowCounter += 1

        # 11 Additional Motion Output Cards_____________
        # "These cards are used only if additional motion output option tag (NMOT) is greater than 0..."
        if self.runOptions["NMOT"].getValue() > 0:
            for n in range(self.runOptions["NMOT"].getValue()):
                rowCounter += 1
                values = lines[rowCounter].split()
                accelerationPoint = {}
                accelerationPoint["XAC"] = float(values[0])
                accelerationPoint["YAC"] = float(values[1])
                accelerationPoint["ZAC"] = float(values[2])
                self.accelerationPoints.append(accelerationPoint)

        # 12 Mooring cards______________________________
        # "...used only if morred ship option tag is greater than 0..."
        # ...

        # 13 Run Control card___________________________
        # A bit funky options on this one, please see the manual...
        rowCounter += 1
        line = lines[rowCounter]
        values = line.split()

        if self.runOptions["ID"].getValue() == 0:
            # In regular waves frequency is given as wave length:
            # Values are [lambda]
            # Lambda [m] --> omega [rad/s]
            self.waveFrequenciesMin = np.sqrt(2 * np.pi * self.g /
                                              float(values[1]))
            self.waveFrequenciesMax = np.sqrt(2 * np.pi * self.g /
                                              float(values[2]))
            self.waveFrequenciesIncrement = np.sqrt(2 * np.pi * self.g /
                                                    float(values[3]))
        else:
            # Values are [rad/s]
            # omega [rad/s] --> omega [rad/s]
            self.waveFrequenciesMin = float(values[1])
            self.waveFrequenciesMax = float(values[2])
            self.waveFrequenciesIncrement = float(values[3])

        self.speedMin = float(values[4]) * 3.6 / 1.852
        self.speedMax = float(values[5]) * 3.6 / 1.852
        self.speedIncrement = float(values[6]) * 3.6 / 1.852

        # 14 Roll damping card__________________________
        # "This card is used only if the degrees of freedom option control tag (IE) is 1 or 2 inticating lateral plane motions calculations are included."
        # ..see manual...
        rowCounter += 1
        values = lines[rowCounter].split(
        )  # This one should probably be devided into a linar and one nonlinear part (remains to be implemented)
        self.partOfCriticalRollDamping = float(values[0])

        # 15 Wave angle card____________________________
        rowCounter += 1
        values = lines[rowCounter].split()
        waveDirectionMinScores = float(values[0])
        waveDirectionMaxScores = float(values[1])

        # Scores uses wave angles that are defined counter clockvise, but the GUI uses regular MDL wave angle def. where 90 deg is port.
        # self.waveDirectionMin = 360 - waveDirectionMaxScores
        # self.waveDirectionMax = 360 - waveDirectionMinScores
        self.waveDirectionMin = waveDirectionMinScores
        self.waveDirectionMax = waveDirectionMaxScores

        self.waveDirectionIncrement = float(values[2])

        # 16 Wave spectra card__________________________
        # "This card appears in the input only for calculations in irregular seas (wave spectra option control tag (ID) is greater than 0)
        rowCounter += 1
        values = lines[rowCounter].split()

        # self.numberOfSeaStates = int(values[0])
        # if self.numberOfSeaStates == len(values) - 1:
        #	if self.runOptions["ID"] == 0:
        #		#Regular waves
        #		pass
        #	elif self.runOptions["ID"] == 1:
        #		#Neuman spectra
        #		pass
        #	elif self.runOptions["ID"] == 2:
        #		#PM spectra
        #		pass
        #	elif self.runOptions["ID"] == 3:
        #		#Two parameter spectra
        #		pass
        #	elif self.runOptions["ID"] == 4:
        #		#Tabulated spectra
        #		pass
        #	elif self.runOptions["ID"] == 5:
        #		#Bretschneider spectra
        #		pass
        #	elif self.runOptions["ID"] == 6:
        #		#Jonswap spectra
        #		Tps = []
        #		for value in values[1:]:
        #			Tps.append(2*np.pi/float(value))
        #		self.Tps = Tps
        # else:
        #	raise ValueError("Not enought specra parameters for %i spectra in row %i" % (self.numberOfSeaStates,rowCounter+1))

        # 17 Tabulated Wave Spectra Cards_______________
        # "These cards and the following set of cards are used only when tabulated wave spectra (Option tag, ID = 4) are to be specified.
        rowCounter += 1
        values = lines[rowCounter].split()
        if self.runOptions["ID"] == 0:
            # Regular waves
            pass
        elif self.runOptions["ID"] == 1:
            # Neuman spectra
            pass
        elif self.runOptions["ID"] == 2:
            # PM spectra
            pass
        elif self.runOptions["ID"] == 3:
            # Two parameter spectra
            pass
        elif self.runOptions["ID"] == 4:
            # Tabulated spectra
            pass
        elif self.runOptions["ID"] == 5:
            # Bretschneider spectra
            pass
        elif self.runOptions["ID"] == 6:
            # Jonswap spectra
            H33s = []
            for value in values:
                H33s.append(float(value))
            self.H33s = H33s

        # 18 Tabulated Wave Spectra Cards_______________
        # ...

        self.lines = lines

    def save(self, indataPath, waveSpectrums=[], b_div_t_max=20, t_div_b_max=10):
        self.indataPath = str(indataPath)

        try:
            file = open(self.indataPath, 'w')
        except:
            return

        # Update the number of wave spectra:
        if self.runOptions["ID"].getValue() == 0:
            self.runOptions["ID"].set_value(len(waveSpectrums))

        # 1  Title Card_________________________________
        file.write("%s\n" % self.projectName)

        # 2  Run option Control Card____________________
        # Try to create the run options control card according to manual page 40-
        for runOptionTag in self.runOptionTags:
            string = str(self.runOptions[runOptionTag].getValue())
            if len(string) < 2:
                string = " " + string
            file.write("%s" % string)
        file.write("\n")

        # 3  Length Card________________________________
        file.write("%-10.3f%-10.3f%-10.5f%-10.1f\n" %
                   (self.lpp, self.rho / 1000, self.g, self.displacement))

        # 4  Hull form cards____________________________
        # The frames in ScoresII are counted from FP, but this GUI uses a traditional numbering from AP so the geomtry vectors have to be reversed.
        bs=np.flipud(self.bs)
        cScores=np.flipud(self.cScores)
        ts=np.flipud(self.ts)
        zbars=np.flipud(self.zbars)

        if not b_div_t_max is None:
            bs,ts=limit_beam_draft_ratio(bs,ts,cScores,b_div_t_max)

        if not t_div_b_max is None:
            bs, ts = limit_draft_beam_ratio(bs, ts, cScores, t_div_b_max)

        if len(zbars)==0:
            raise pyscores2.ZbarsMissingError()

        for b, cScores, t, zbar in zip(bs, cScores, ts, zbars):
            file.write("%-10.4f%-10.4f%-10.4f%-10.4f\n" % (b, cScores, t, zbar))


        # 5  Section Card_______________________________
        # (Needed only if close-fitted option IM > 0
        # ...

        # 6  Section offset card_______________________
        # "These cards appear in the input only if the closefit option tag (IM) is greater than zero..."

        # 7  Lateral plane card________________________
        file.write("%-10.2f%-10.2f\n" % (self.zcg, self.kxx))

        # 8  Longitudinal total mass properties card____
        # "This card is used only if the moment option tag IB is 0..."
        faktor = -(self.lcb-self.lpp/2)
        file.write("%-10.2f%-10.2f\n" % (self.kyy, faktor))

        # 9  Sectional mass properties__________________
        # ...

        # 10 Vertical Bending Moment Station and...
        # "...needed only if the degrees of freeedom option tag (IE) is 0 or 1.
        # ...."
        file.write("%s\n" % "         0        10         1")

        # 11 Additional Motion Output Cards_____________
        # "These cards are used only if additional motion output option tag (NMOT) is greater than 0..."
        for accelerationPoint in self.accelerationPoints:
            file.write("%10.5f%10.5f%10.5f\n" %
                       (accelerationPoint["XAC"], accelerationPoint["YAC"],
                        accelerationPoint["ZAC"]))

        # 12 Mooring cards______________________________
        # "...used only if morred ship option tag is greater than 0..."
        # ...

        # 13 Run Control card___________________________
        # A bit funky options on this one, please see the manual...

        if self.runOptions["ID"].getValue() == 0:
            # In regular waves frequency is given as wave length:
            # Values should be [lambda]
            # omega [rad/s] --> lambda [m]
            waveFrequenciesMin = 2 * np.pi * self.g / (
                self.waveFrequenciesMax) ** 2
            waveFrequenciesMax = 2 * np.pi * self.g / (
                self.waveFrequenciesMin) ** 2

            N=(self.waveFrequenciesMax - self.waveFrequenciesMin)/self.waveFrequenciesIncrement

            waveFrequenciesIncrement = (waveFrequenciesMax - waveFrequenciesMin)/N

        else:
            # Values should be [1/T]
            # omega [rad/s] --> omega [rad/s]

            waveFrequenciesMin = self.waveFrequenciesMin
            waveFrequenciesMax = self.waveFrequenciesMax
            waveFrequenciesIncrement = self.waveFrequenciesIncrement

        file.write(
            "1.0       %-10.2f%-10.2f%-10.2f%-10.2f%-10.4f%-10.4f\n" %
            (waveFrequenciesMin, waveFrequenciesMax, waveFrequenciesIncrement,
             self.speedMin * 1.852 / 3.6, self.speedMax * 1.852 / 3.6,
             self.speedIncrement * 1.852 / 3.6))

        # 14 Roll damping card__________________________
        # "This card is used only if the degrees of freedom option control tag (IE) is 1 or 2 inticating lateral plane motions calculations are included."
        # ..see manual...
        file.write("%-10.4f\n" % self.partOfCriticalRollDamping)

        # 15 Wave angle card____________________________
        # Scores uses wave angles that are defined counter clockvise, but the GUI uses regular MDL wave angle def. where 90 deg is port.
        #waveDirectionMinScores = 360 - self.waveDirectionMax
        #waveDirectionMaxScores = 360 - self.waveDirectionMin
        waveDirectionMinScores = self.waveDirectionMin
        waveDirectionMaxScores = self.waveDirectionMax

        file.write("%-10.1f%-10.1f%-10.1f\n" %
                   (waveDirectionMinScores, waveDirectionMaxScores,
                    self.waveDirectionIncrement))

        # 16 Wave spectra card__________________________
        # "This card appears in the input only for calculations in irregular seas (wave spectra option control tag (ID) is greater than 0)
        if len(waveSpectrums) > 0:

            # Go through the wave spectrum list and find only the ones that are of the kind that corresponds to the wave spectrum option flag:
            wantedSpectrumID = int(self.runOptions["ID"].getValue())
            wantedSpectrums = []
            counter = 0
            for waveSpectrum in waveSpectrums:
                if waveSpectrum.scoresFileID == wantedSpectrumID:
                    if counter <= 5:  # Max 5 spectra alowed in scoresII
                        wantedSpectrums.append(waveSpectrum)
                        counter += 1
                    else:
                        break

            file.write("%10i " % len(wantedSpectrums))

            for waveSpectrum in wantedSpectrums:
                parameters = waveSpectrum.getParameters()
                file.write("%-5.2f" % (parameters[0]))

            file.write("\n")
            file.write("          ")

            for waveSpectrum in wantedSpectrums:
                parameters = waveSpectrum.getParameters()
                file.write("%-5.2f" % (parameters[1]))
            file.write("\n")

        else:
            file.write("0\n")

        # 17 Tabulated Wave Spectra Cards_______________
        # "These cards and the following set of cards are used only when tabulated wave spectra (Option tag, ID = 4) are to be specified.
        # file.write("%s\n" % "          1.5  2.5  3.5  4.5  5.5  ")

        # 18 Tabulated Wave Spectra Cards_______________
        file.write("%s\n" % "-1.0")

        # End Stuff
        file.write("%s\n" % "/*")
        file.write("%s\n" % "//")

        file.close()


def limit_section_ratio(b, t, cScores, ratio_max=20):
    b_new, t_new = limit_beam_draft_ratio(b, t, cScores, b_div_t_max=ratio_max)
    b_newer, t_newer = limit_draft_beam_ratio(b_new, t_new, cScores, t_div_b_max=ratio_max)
    return b_newer, t_newer

def limit_beam_draft_ratio(b, t, cScores, b_div_t_max=20):
    return _limit_beam_draft_ratio(b, t, cScores, b_div_t_max=b_div_t_max)

def limit_draft_beam_ratio(b, t, cScores, t_div_b_max=20):
    t_new, b_new = _limit_beam_draft_ratio(t, b, cScores, b_div_t_max=t_div_b_max)
    return b_new, t_new

def _limit_beam_draft_ratio(b, t, cScores, b_div_t_max=20):
    """
    Sometimes the sections have too high beam to draught ratios b/t.
    :param b:
    :param t:
    :param cScores:
    :param b_div_t_max:
    :return: b_new, t_new
    """

    t_new = np.array(t, dtype=float)
    b_new = np.array(b, dtype=float)

    mask = np.divide(b_new, t_new, out=np.ones_like(b_new)*1.1*b_div_t_max, where=t_new!=0) > b_div_t_max  # Too large beam/draught ratios...
    # b*t*cScores=area
    # -->b=area/(t*cScores)
    # t=b/b_div_t_max
    # -->t=(area/(t*cScores))/b_div_t_max
    # -->t^2=(area/(cScores))/b_div_t_max
    # -->t=sqrt((area/(cScores))/b_div_t_max)

    area=b[mask]*t[mask]*cScores[mask]
    t_new[mask] = np.sqrt((area / (cScores[mask])) / b_div_t_max)
    b_new[mask] = t_new[mask] * b_div_t_max

    return b_new, t_new

class RunOption(object):
    """This is a class that stores a run option"""

    def __init__(self, description=""):

        self.description = description
        self.alternatives = []
        self.value = False

    def addOption(self, description=""):
        self.alternatives.append(RunOption(description=description))

    def getValue(self):
        """Retrieves the value of the option, either its value or it's choosen suboption"""
        if len(self.alternatives) > 0:
            counter = 0
            for alternative in self.alternatives:
                if alternative.value:
                    return counter
                counter += 1
        else:
            return self.value

    def set_value(self, value=None):
        if len(self.alternatives) > 0:
            if type(value) == type(int()):
                subAlternative = value
                if subAlternative >= 0 and subAlternative < len(
                        self.alternatives):
                    for alternative in self.alternatives:
                        alternative.value = False

                    self.alternatives[subAlternative].value = True
                else:
                    raise ValueError("Subalternative %i does not exist" %
                                     subAlternative)
            else:
                raise ValueError("Suboption must be an integer value")
        else:
            self.value = value


def intSpecial(string):
    # The only special thing about this function is that it also converts  whitespaces "   " to 0:
    if len(string.split()) == 0:
        # Only Whitespaces...
        return 0
    else:
        return int(string)
