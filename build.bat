@echo off
REM ---------------------------------------------------------------------
REM Compila entrambi gli eseguibili in dist\
REM   merge_pdf-cli.exe : versione console
REM   merge_pdf-gui.exe : versione grafica
REM ---------------------------------------------------------------------

echo [1/2] Build versione CLI...
pyinstaller --onefile --console --name merge_pdf-cli cli_main.py
if errorlevel 1 goto :error

echo [2/2] Build versione GUI...
pyinstaller --onefile --windowed --name merge_pdf-gui gui_main.py
if errorlevel 1 goto :error

echo.
echo Build completata. Eseguibili in dist\
goto :eof

:error
echo.
echo Build fallita.
exit /b 1
