@echo off
REM Find Chrome Extensions - Helper Script
REM This script helps locate installed Chrome extensions

echo ========================================
echo Chrome Extension Path Finder
echo ========================================
echo.

set CHROME_EXTENSIONS=%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions

if not exist "%CHROME_EXTENSIONS%" (
    echo ERROR: Chrome extensions folder not found!
    echo Expected location: %CHROME_EXTENSIONS%
    echo.
    echo Please verify Chrome is installed and you've run it at least once.
    pause
    exit /b 1
)

echo Chrome Extensions Directory:
echo %CHROME_EXTENSIONS%
echo.
echo ========================================
echo Installed Extensions:
echo ========================================
echo.

REM List all extension folders
for /d %%G in ("%CHROME_EXTENSIONS%\*") do (
    echo Extension ID: %%~nxG
    
    REM List versions for this extension
    for /d %%V in ("%%G\*") do (
        echo   Version: %%~nxV
        echo   Full Path: %%V
        
        REM Check if manifest.json exists
        if exist "%%V\manifest.json" (
            echo   Status: Valid ^(manifest.json found^)
            
            REM Try to extract extension name from manifest
            findstr /C:"\"name\"" "%%V\manifest.json" > nul
            if not errorlevel 1 (
                for /f "tokens=2 delims=:," %%N in ('findstr /C:"\"name\"" "%%V\manifest.json"') do (
                    set "EXT_NAME=%%N"
                    setlocal enabledelayedexpansion
                    echo   Name: !EXT_NAME:"=!
                    endlocal
                )
            )
        ) else (
            echo   Status: Invalid ^(no manifest.json^)
        )
        echo.
    )
    echo ----------------------------------------
    echo.
)

echo ========================================
echo How to Use:
echo ========================================
echo.
echo 1. Look for "AEM Sidekick" or your desired extension in the list above
echo 2. Copy the "Full Path" shown
echo 3. Paste it into the Visual QA Tool's "Extension Path" field
echo.
echo Example path format:
echo C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\abcdef123456\1.0.0
echo.
echo ========================================
echo.

REM Offer to search for specific extension
echo.
set /p SEARCH_NAME="Enter extension name to search for (or press Enter to skip): "

if not "%SEARCH_NAME%"=="" (
    echo.
    echo Searching for: %SEARCH_NAME%
    echo.
    
    for /d %%G in ("%CHROME_EXTENSIONS%\*") do (
        for /d %%V in ("%%G\*") do (
            if exist "%%V\manifest.json" (
                findstr /I /C:"%SEARCH_NAME%" "%%V\manifest.json" > nul
                if not errorlevel 1 (
                    echo FOUND: %%V
                    echo Extension ID: %%~nxG
                    echo Version: %%~nxV
                    echo.
                )
            )
        )
    )
)

echo.
pause
