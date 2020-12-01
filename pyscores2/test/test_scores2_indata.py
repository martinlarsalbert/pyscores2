import pytest
import pyscores2
import os
import numpy as np
from pyscores2.indata import Indata, limit_beam_draft_ratio, limit_section_ratio
from numpy.testing import assert_almost_equal
import pyscores2.test

temp_in_path = os.path.join(pyscores2.test.path,'temp.in')

def test_open_indata():
    indata = Indata()
    indata.open(temp_in_path)
    assert indata.kxx == 15


def test_open_and_save_indata(tmpdir):
    indata = Indata()
    indata.open(temp_in_path)
    new_file_path = os.path.join(str(tmpdir), 'test.in')
    indata.save(indataPath=new_file_path)

    indata2 = Indata()
    indata2.open(new_file_path)

    assert indata.lpp == indata2.lpp

def test_open_and_save_indata2(tmpdir):
    indata = Indata()
    indata.open(temp_in_path)
    indata.waveDirectionIncrement = 12
    indata.waveDirectionMin = 2
    indata.waveDirectionMax = 24

    new_file_path = os.path.join(str(tmpdir), 'test.in')
    indata.save(indataPath=new_file_path)

    indata2 = Indata()
    indata2.open(new_file_path)

    assert indata2.waveDirectionIncrement == 12
    assert indata2.waveDirectionMin == 2
    assert indata2.waveDirectionMax == 24

def test_limit_section_ratio():

    N = 2
    b = np.ones(N)
    ratios = np.array([30,15])
    t = b/ratios
    cScores = 0.9*np.ones(N)

    ratio_max=20
    b_new, t_new = limit_section_ratio(b=b,t=t, cScores=cScores, ratio_max=ratio_max)

    ratios_desired = np.array([20, 15])
    assert_almost_equal(b_new/t_new,ratios_desired)
    assert_almost_equal(b_new*t_new*cScores, b*t*cScores)

    assert_almost_equal(b_new[1], b[1])
    assert_almost_equal(t_new[1], t[1])

def test_limit_section_ratio():

    N = 2
    b = np.ones(N)
    ratios = np.array([30,15])
    t = b/ratios
    cScores = 0.9*np.ones(N)

    ratio_max=20
    b_new, t_new = limit_section_ratio(b=b,t=t, cScores=cScores, ratio_max=ratio_max)

    ratios_desired = np.array([20, 15])
    assert_almost_equal(b_new/t_new,ratios_desired)
    assert_almost_equal(b_new*t_new*cScores, b*t*cScores)

    assert_almost_equal(b_new[1], b[1])
    assert_almost_equal(t_new[1], t[1])

def test_limit_section_ratio2():

    N = 2
    b = np.ones(N)
    ratios = np.array([30,1/30])
    t = b/ratios
    cScores = 0.9*np.ones(N)

    ratio_max=20
    b_new, t_new = limit_section_ratio(b=b,t=t, cScores=cScores, ratio_max=ratio_max)

    ratios_desired = np.array([20, 1/20])
    assert_almost_equal(b_new/t_new,ratios_desired)
    assert_almost_equal(b_new*t_new*cScores, b*t*cScores)





