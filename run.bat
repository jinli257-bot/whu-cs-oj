@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PYEXE="
set "PYARG="

py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
  set "PYEXE=py"
  set "PYARG=-3"
)

if not defined PYEXE (
  python -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    for /f "delims=" %%v in ('python -c "import sys;print(sys.version_info[0])" 2^>nul') do (
      if "%%v"=="3" set "PYEXE=python"
    )
  )
)

rem 本机 DSH 自带的 Python 作为兜底（普通用户机器上通常不存在，会跳过）
if not defined PYEXE (
  set "BUNDLED=%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
  if exist "%BUNDLED%" (
    "%BUNDLED%" -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYEXE=%BUNDLED%"
  )
)

if not defined PYEXE (
  echo.
  echo [错误] 没有找到可用的 Python 3。
  echo 请安装 Python 3.10 或更高版本，安装时勾选 "Add Python to PATH"。
  echo 下载地址：https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)

echo 正在启动珞珈机试 OJ...
"%PYEXE%" %PYARG% server.py --open %*
if errorlevel 1 pause
