@echo off

set APPLICATION=Labview.exe

for /F "tokens=*" %%i in ('netsh advfirewall firewall show rule "%APPLICATION%" ^| findstr /R "Enabled.*Yes"') do set result=%%i

if "%result%"=="" (
  echo Adding firewall exeption for %APPLICATION%
  netsh advfirewall firewall add rule name="APPLICATION" dir=in action=allow program="%~dp0%APPLICATION%"
) else (
  echo Firewall exeption for %APPLICATION% already exists
)

pause
