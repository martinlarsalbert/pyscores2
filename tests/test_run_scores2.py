import pytest
from pyscores2.runScores2 import Calculation

@pytest.fixture
def calculation(tmpdir):
    outdata_directory = str(tmpdir)
    calculation = Calculation(indataPath='temp.in', outDataDirectory=outdata_directory)
    yield calculation


def test_run(calculation):

    calculation.run()



