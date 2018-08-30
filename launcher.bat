@echo off
title Fbx2Mitsuba
echo Welcome to Fbx2Mitsuba !
if not "%~1"=="" goto args
: setupfile
echo You have to chose a file to be converted.
echo The launcher will now exit, you just have to drag and drop the fbx file on the launcher.bat file.
pause
goto eof
: args
echo Type in arguments you would like to add, else simply hit enter.
echo Type "help" for a list of arguments and their description.
set /P arguments=""
if not "%arguments%"=="help" goto execution
: help
echo Type all arguments separated with spaces. Available arguments are :
echo -v or --verbose : verbose mode, the converter will give more details about what is happening.
echo -d or --debug : the fbx file will be exported as file_fbx.xml. Can take very long for big files.
echo --closest or --realist : Mutually exclusive options to prioritize fidelity to the original scene or realism.
echo --portable : Uses relative
goto args
: execution
echo Pillow installation...
pip install Pillow
python %~dp0\converter.py "%~1" "%arguments%"
pause
