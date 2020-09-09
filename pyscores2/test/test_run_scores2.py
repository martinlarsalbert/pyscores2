import pytest
from pyscores2.runScores2 import Calculation

@pytest.fixture
def calculation(tmpdir):
    outdata_directory = str(tmpdir)
    calculation = Calculation(indataPath='temp.in', outDataDirectory=outdata_directory)
    yield calculation


def test_run(calculation):
    calculation.run()

def test_get_result_no_run(calculation):
    with pytest.raises(ValueError):
        calculation.getResult()

def test_get_result(calculation):
    calculation.run()
    added_resistance_RAOs = calculation.getResult()
    assert added_resistance_RAOs[181][0].responses == 0.975603955801746


