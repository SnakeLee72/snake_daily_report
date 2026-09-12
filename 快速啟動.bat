@echo off
chcp 65001 >nul
title Snake Daily Report - 自動排程與執行助手

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請確認已安裝 Python 3.11/3.12 並加入系統 PATH。
    echo.
    pause
    exit /b 1
)

python setup_task.py
if errorlevel 1 (
    echo.
    echo [提示] 執行中斷或發生異常。
    pause
)
