@echo off
title Create Runtime
cd /d "%~dp0"

echo Downloading Python...
curl -o pyemb.zip https://www.python.org/ftp/python/3.13.7/python-3.13.7-embed-amd64.zip 
powershell -Command "Expand-Archive -Path pyemb.zip -DestinationPath runtime -Force"
if not "%ERRORLEVEL%"=="0" goto err
del /q pyemb.zip
if not "%ERRORLEVEL%"=="0" goto err
set PATH=%~dp0\runtime;%PATH%

echo Getting PIP...
cd runtime
curl -O https://bootstrap.pypa.io/get-pip.py
if not "%ERRORLEVEL%"=="0" goto err
python get-pip.py
if not "%ERRORLEVEL%"=="0" goto err
echo Adjusting python313._pth
echo import site >> python313._pth
cd ..

echo Installing requirements...
set PATH=%~dp0\runtime\Scripts;%PATH%
python -m pip install -r ./requirements.txt
if not "%ERRORLEVEL%"=="0" goto err

echo Runtime created!
timeout /t 600
goto eof

:err
echo FAILED!!
timeout /t 3600
goto eof
