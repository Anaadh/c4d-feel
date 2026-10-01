@echo off
rem Runs build_fork.cmd at low priority, logging to %USERPROFILE%\fork_build.log
call "%~dp0build_fork.cmd" %1 > "%USERPROFILE%\fork_build.log" 2>&1
echo EXIT %ERRORLEVEL% >> "%USERPROFILE%\fork_build.log"
