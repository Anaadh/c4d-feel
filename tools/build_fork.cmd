@echo off
rem Throttled build of the C4D Blender fork (Ninja, limited jobs, low priority).
rem Usage: build_fork.cmd [jobs]   (default 8)
rem Output: %USERPROFILE%\build_c4d\bin\blender.exe

setlocal
set JOBS=%1
if "%JOBS%"=="" set JOBS=8
set SRC=%USERPROFILE%\blender-fork
set BUILD=%USERPROFILE%\build_c4d
set VS=C:\Program Files\Microsoft Visual Studio\2022\Community

call "%VS%\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set PATH=%VS%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;%VS%\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin;%PATH%

python "%USERPROFILE%\blender-c4d\tools\sync_to_fork.py" "%SRC%" || exit /b 1

if not exist "%BUILD%\build.ninja" (
  cmake -G Ninja -S "%SRC%" -B "%BUILD%" ^
    -C "%SRC%\build_files\cmake\config\blender_release.cmake" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX="%BUILD%\bin" ^
    -DWITH_CYCLES_CUDA_BINARIES=OFF ^
    -DWITH_CYCLES_HIP_BINARIES=OFF ^
    -DWITH_CYCLES_ONEAPI_BINARIES=OFF ^
    -DWITH_CYCLES_DEVICE_HIPRT=OFF || exit /b 1
)

ninja -C "%BUILD%" -j %JOBS% install || exit /b 1
echo BUILD_OK
