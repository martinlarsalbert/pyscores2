@echo off
echo This script will test and deploy Evaluation as a package to SSPA pypi server
echo Activating venv
call venv\Scripts\activate.bat
echo Deploy to SSPA pypi server
call python setup.py bdist_wheel upload -r buildmaster

pause