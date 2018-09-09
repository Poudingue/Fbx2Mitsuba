@echo off
title Fbx2Mitsuba
echo Welcome to Fbx2Mitsuba !
if not "%~1"=="" goto execution
: setupfile
echo You have to chose a file to be converted.
echo The launcher will now exit, you just have to drag and drop the fbx file on the launcher.bat file.
pause
goto eof
: execution
echo Pillow installation...
pip install Pillow
python "%~dp0\converter.py" "%~1" "-v"
pause
