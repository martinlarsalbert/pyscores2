import pytest
from pyscores2.scorseFileParser import scorseFileClass

def test_load_file():

    scores_file = scorseFileClass(filePath='temp.out')
    assert hasattr(scores_file,'results')
    assert 181 in scores_file.results
    assert 0 in scores_file.results[181]
    assert hasattr(scores_file.results[181][0],'addedResistance')

@pytest.fixture
def scores_file():
    yield scorseFileClass(filePath='temp.out')

def test_load_roll_damping(scores_file):

    result = scores_file.results[181][90]
    assert result.calculated_wave_damping_in_roll==3264.0

    a = 1




