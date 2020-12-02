from pyscores2 import xml_hydrostatics
import os.path
import pyscores2.test
from pyscores2.runScores2 import Calculation
from pyscores2.test.test_run_scores2 import calculation

def test_parse_hydostratics():
    file_path = os.path.join(pyscores2.test.path,'hydrostatics.xml')
    xml_parser = xml_hydrostatics.Parser(fileName=file_path)
    conditions = list(xml_parser.conditions.keys())
    indata = xml_parser.convertToScores2Indata(conditionName=conditions[0])

def test_parse_hydostratics_and_run(calculation):
    file_path = os.path.join(pyscores2.test.path,'hydrostatics.xml')
    xml_parser = xml_hydrostatics.Parser(fileName=file_path)
    conditions = list(xml_parser.conditions.keys())
    indata = xml_parser.convertToScores2Indata(conditionName=conditions[0])


    calculation.run(indata=indata)

