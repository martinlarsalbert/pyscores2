import pytest
import pyscores2
import os
from pyscores2.indata import Indata


def test_open_indata():
    indata = Indata()
    indata.open('temp.in')
    assert indata.kxx == 15


def test_open_and_save_indata(tmpdir):
    indata = Indata()
    indata.open('temp.in')
    new_file_path = os.path.join(str(tmpdir), 'test.in')
    indata.save(indataPath=new_file_path)

    indata2 = Indata()
    indata2.open(new_file_path)

    assert indata.lpp == indata2.lpp

def test_open_and_save_indata2(tmpdir):
    indata = Indata()
    indata.open('temp.in')
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