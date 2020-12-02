from pyscores2 import xml_hydrostatics
import os.path
import pyscores2.test
from pyscores2.runScores2 import Calculation
from pyscores2.test.test_run_scores2 import calculation
import numpy as np

def test_parse_hydostratics():
    file_path = os.path.join(pyscores2.test.path,'KVLCC2m_kbk_final_ScoresData.xml')
    xml_parser = xml_hydrostatics.Parser(fileName=file_path)
    conditions = list(xml_parser.conditions.keys())
    indata = xml_parser.convertToScores2Indata(conditionName=conditions[0])

def test_parse_hydostratics_and_run(calculation):
    file_path = os.path.join(pyscores2.test.path,'KVLCC2m_kbk_final_ScoresData.xml')
    xml_parser = xml_hydrostatics.Parser(fileName=file_path)
    indata = xml_parser.convertToScores2Indata(conditionName='Design')

    indata.kxx = 10
    indata.kyy = indata.lpp*0.3
    indata.zcg = 1
    indata.partOfCriticalRollDamping = 0.0850
    indata.runOptions["IJ"].set_value(1)
    indata.runOptions["IK"].set_value(2)
    indata.waveDirectionMin=180.0
    indata.waveDirectionMax=360.0
    indata.waveDirectionIncrement=30.0
    #indata.zbars = list(np.zeros(21))
    
    #indata.bs[1]=6.0
    #indata.bs[-1]=1.0
    
    #indata.ts[1]=1.0
    #indata.ts[0]=1.0
    

    #indata.ts[-1]=1.0
    #indata.cScores[1]=0.5
    #indata.cScores[-1]=0.5

    calculation.run(indata=indata)

