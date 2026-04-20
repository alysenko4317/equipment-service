@echo off
setlocal enabledelayedexpansion

echo === Hash calculation for *.bin files ===
echo.

for %%f in (*.bin) do (
echo File: %%f

echo   MD5:
certutil -hashfile "%%f" MD5 | find /v "hashfile" | find /v "CertUtil"

echo   SHA1:
certutil -hashfile "%%f" SHA1 | find /v "hashfile" | find /v "CertUtil"

echo   SHA256:
certutil -hashfile "%%f" SHA256 | find /v "hashfile" | find /v "CertUtil"

echo.

)

echo Done.
pause
