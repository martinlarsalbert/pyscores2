import pytest
from pyscores2.output import OutputFile


def test_load_file():

    scores_file = OutputFile(filePath='temp.out')
    assert hasattr(scores_file, 'results')
    assert 181 in scores_file.results
    assert 0 in scores_file.results[181]
    assert hasattr(scores_file.results[181][0], 'addedResistance')


@pytest.fixture
def scores_file():
    yield OutputFile(filePath='temp.out')


def test_load_roll_damping(scores_file):

    result = scores_file.results[181][90]
    assert result.calculated_wave_damping_in_roll == 3264.0


def test_get_result_for_one_speed_and_wave(scores_file):
    result = scores_file.results[181][90]
    df = result.get_result()


def test_get_result_for_all(scores_file):
    df = scores_file.get_result()
    a = 1
