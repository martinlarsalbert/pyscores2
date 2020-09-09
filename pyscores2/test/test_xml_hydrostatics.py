from pyscores2 import xml_hydrostatics


def test_parse_hydostratics():
    xml_parser = xml_hydrostatics.Parser('hydrostatics.xml')
    conditions = list(xml_parser.conditions.keys())
    indata = xml_parser.convertToScores2Indata(conditionName=conditions[0])
    a = 1
