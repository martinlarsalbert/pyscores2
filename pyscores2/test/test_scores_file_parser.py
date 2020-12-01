import pytest
from pyscores2.output import OutputFile
import pyscores2.test
import os

def test_load_file():

    scores_file = OutputFile(filePath=pyscores2.test.outdata_path)
    assert hasattr(scores_file, 'results')
    assert 181 in scores_file.results
    assert 180 in scores_file.results[181]
    assert hasattr(scores_file.results[181][180], 'addedResistance')


@pytest.fixture
def scores_file():
    yield OutputFile(filePath=pyscores2.test.outdata_path)

@pytest.fixture
def scores_file_S175():
    yield OutputFile(filePath=os.path.join(pyscores2.test.path,'S175.out'))


def test_load_roll_damping(scores_file):

    result = scores_file.results[181][270]
    assert result.calculated_wave_damping_in_roll == 3264.0


def test_get_result_for_one_speed_and_wave(scores_file):
    result = scores_file.results[181][270]
    df = result.get_result()


def test_get_result_for_all(scores_file):
    df = scores_file.get_result()
    a = 1

def test_get_roll_damping_all(scores_file):
    df = scores_file.get_roll_damping()
    a = 1

def test_get_section_coefficients(scores_file_S175):
    df_sections = scores_file_S175.get_section_coefficients()