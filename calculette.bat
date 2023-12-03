:home
@echo off
echo Type a number.
set /p one=
cls
echo Type the sign. (+,-,*,/)
set :p two=%one%
echo And type the last number.
set /p three=%one%%two%
set /a final=%one%%two%%three%
cls
echo Total:
echo %one%%two%%three%=%final%
pause
cls
goto home
