import pytest
import pyscores2
import os
from pyscores2.indata import Indata

def test_open_indata():
    indata = Indata()
    indata.open('temp.in')
    assert indata.kxx==15

def test_open_and_save_indata(tmpdir):
    indata = Indata()
    indata.open('temp.in')
    new_file_path=os.path.join(str(tmpdir),'test.in')
    indata.save(indataPath=new_file_path)

    indata2 = Indata()
    indata2.open(new_file_path)

    assert indata.lpp==indata2.lpp


