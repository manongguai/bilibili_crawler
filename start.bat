@echo off
chcp 65001 >nul
title B站视频爬虫

echo 🎬 B站视频爬虫程序
echo ==================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查requests是否安装
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖...
    python -m pip install requests --user
)

echo.
echo 🚀 启动爬虫程序...
echo.

REM 运行爬虫程序
if "%~1"=="" (
    python run.py
) else (
    python run.py %1
)

pause