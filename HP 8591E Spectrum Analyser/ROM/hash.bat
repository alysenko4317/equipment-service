@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::  hash.bat  -  Compute MD5 / SHA-1 / SHA-256 for all *.bin files and save
::               results to  md5.txt  in the same target folder.
::
::  Usage (from the ROM root):
::    hash.bat "98-06-15 - copy 1"   <- hash files in that subfolder
::    hash.bat                        <- hash *.bin files in the current dir
::
::  Usage (double-click from inside a chip-dump folder):
::    hash.bat                        <- hashes *.bin files right here
::
::  Output format (also written to md5.txt in the target folder):
::    u24.bin
::      MD5    0b11704fe6a522ea74dad13f966a8b96
::      SHA1   10cc6ad77e8d0053e1e8d75dbce46d6b8e276def
::      SHA256 13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73
::
::  Requires: Windows built-in  certutil  (present on all modern Windows).
:: ============================================================================

:: ── resolve target directory ──────────────────────────────────────────────

if "%~1"=="" (
    set "DIR=%CD%"
) else (
    :: resolve to absolute path, strip trailing backslash
    set "DIR=%~f1"
)

set "OUT=%DIR%\md5.txt"

:: ── sanity check ──────────────────────────────────────────────────────────

set "COUNT=0"
for %%f in ("%DIR%\*.bin") do set /a COUNT+=1

if %COUNT%==0 (
    echo No .bin files found in:
    echo   %DIR%
    echo.
    pause
    exit /b 1
)

echo Computing hashes for %COUNT% .bin file(s) in:
echo   %DIR%
echo.

:: ── create / overwrite output file ───────────────────────────────────────

type nul > "%OUT%"

:: ── loop over every .bin file ─────────────────────────────────────────────

for %%F in ("%DIR%\*.bin") do (
    set "FNAME=%%~nxF"

    :: --- MD5 ---
    set "_h="
    for /f "skip=1 tokens=*" %%x in ('certutil -hashfile "%%F" MD5 2^>nul') do (
        if not defined _h set "_h=%%x"
    )
    set "HASH_MD5=!_h!"

    :: --- SHA-1 ---
    set "_h="
    for /f "skip=1 tokens=*" %%x in ('certutil -hashfile "%%F" SHA1 2^>nul') do (
        if not defined _h set "_h=%%x"
    )
    set "HASH_SHA1=!_h!"

    :: --- SHA-256 ---
    set "_h="
    for /f "skip=1 tokens=*" %%x in ('certutil -hashfile "%%F" SHA256 2^>nul') do (
        if not defined _h set "_h=%%x"
    )
    set "HASH_SHA256=!_h!"

    :: --- print to console ---
    echo !FNAME!
    echo   MD5    !HASH_MD5!
    echo   SHA1   !HASH_SHA1!
    echo   SHA256 !HASH_SHA256!
    echo.

    :: --- append to md5.txt ---
    >> "%OUT%" echo !FNAME!
    >> "%OUT%" echo   MD5    !HASH_MD5!
    >> "%OUT%" echo   SHA1   !HASH_SHA1!
    >> "%OUT%" echo   SHA256 !HASH_SHA256!
    >> "%OUT%" echo.
)

echo Saved to:
echo   %OUT%
echo.
pause

