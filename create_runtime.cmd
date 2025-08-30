@echo off
title Create Runtime
cd /d "%~dp0"

echo Downloading Python...
curl -o pyemb.zip https://www.python.org/ftp/python/3.13.7/python-3.13.7-embed-amd64.zip 
powershell -Command "Expand-Archive -Path pyemb.zip -DestinationPath runtime -Force"
del /q pyemb.zip
set PATH=%~dp0\runtime;%PATH%

echo Getting PIP...
cd runtime
curl -O https://bootstrap.pypa.io/get-pip.py
python get-pip.py
cd ..

echo Installing requirements...
set PATH=%~dp0\runtime\Scripts;%PATH%
python -m pip install -r ../requirements.txt

echo Runtime created!
timeout /t 600
