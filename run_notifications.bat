@echo off
pushd "%~dp0"
if exist "%~dp0\.venv\Scripts\activate.bat" (
    call "%~dp0\.venv\Scripts\activate.bat"
)
"%~dp0\.venv\Scripts\python.exe" "%~dp0\desktop_launcher.py"
set "exitCode=%ERRORLEVEL%"
if not "%exitCode%" == "0" pause
popd
exit /b %exitCode%
