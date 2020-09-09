import pytest
from pyscores2.runScores2 import scores2CalculationClass

@pytest.fixture
def calculation(tmpdir):
    outdata_directory = str(tmpdir)
    calculation = scores2CalculationClass(indataPath='temp.in', outDataDirectory=outdata_directory)
    yield calculation


def test_run(calculation):

    calculation.runScores2()



