@echo off
chcp 65001 >nul
title Snake Daily Report - 快速生成日報 (Copilot 365 模式)

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請確認已安裝 Python 並加入系統 PATH。
    echo.
    pause
    exit /b 1
)

echo ======================================================================
echo   Snake Daily Report - 快速生成日報
echo   模式：Copilot 365 視窗自動化
echo   主題：全部 5 大分類（50 則主題全收錄）
echo   寄信：否（不寄送郵件）
echo ======================================================================
echo.

python main.py --mode copilot

echo.
echo ======================================================================
echo [完成] 日報生成作業已結束。
echo ======================================================================
echo.
pause