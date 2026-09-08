@echo off
chcp 65001 >nul
title Snake Daily Report - Windows 11 工作排程設定精靈

echo ======================================================================
echo           Snake Daily Report - 每日定時自動化工作排程精靈
echo ======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請確認已安裝 Python 3.11/3.12 並加入系統 PATH。
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do (
    set "PYTHON_EXE=%%i"
    goto :found_python
)

:found_python
echo [環境資訊]
echo - 專案路徑: %SCRIPT_DIR%
echo - Python  : %PYTHON_EXE%
echo.

net session >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] 註冊 Windows 工作排程需使用「系統管理員身分」。
    echo 正在嘗試自動請求以管理員身分重新啟動...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/k `"%~f0`"' -Verb RunAs"
    exit /b
)

echo 請選擇要執行的功能：
echo [1] 建立每日自動排程 (預設每日 08:30 執行)
echo [2] 立即測試手動執行一次日報
echo [3] 查詢排程任務狀態
echo [4] 刪除此排程任務
echo [5] 離開
echo.
set /p CHOICE="請輸入選項 [1-5，預設 1]: "
if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" goto :CREATE_TASK
if "%CHOICE%"=="2" goto :RUN_NOW
if "%CHOICE%"=="3" goto :QUERY_TASK
if "%CHOICE%"=="4" goto :DELETE_TASK
if "%CHOICE%"=="5" exit /b
goto :MENU_END

:CREATE_TASK
echo.
set /p EXEC_TIME="請輸入每日執行時間 [格式 HH:mm，如 08:30]: "
if "%EXEC_TIME%"=="" set EXEC_TIME=08:30

echo.
echo 請選擇執行模式：
echo [1] Copilot 365 視窗自動化 (同聊天室連續 50 題)
echo [2] Direct 即時快速模式 (無介面秒級產出，最適合背景排程)
set /p MODE_CHOICE="請輸入模式 [1 或 2，預設 1]: "
set "RUN_MODE=copilot"
if "%MODE_CHOICE%"=="2" set "RUN_MODE=direct"

set "TASK_NAME=SnakeDailyReport"
set "RUN_CMD="%PYTHON_EXE%" "%SCRIPT_DIR%main.py" --mode %RUN_MODE%"

echo.
echo 正在向 Windows 工作排程器註冊任務 [%TASK_NAME%]...
schtasks /create /tn "%TASK_NAME%" /tr "%RUN_CMD%" /sc DAILY /st %EXEC_TIME% /f

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo [成功] 每日定時工作排程已設定完成！
    echo - 任務名稱: %TASK_NAME%
    echo - 執行時間: 每天 %EXEC_TIME%
    echo - 執行命令: %RUN_CMD%
    echo ======================================================================
) else (
    echo.
    echo [失敗] 註冊工作排程失敗，請確認已使用系統管理員身分執行。
)
pause
exit /b

:RUN_NOW
echo.
echo 正在啟動 Snake Daily Report...
"%PYTHON_EXE%" "%SCRIPT_DIR%main.py"
pause
exit /b

:QUERY_TASK
echo.
schtasks /query /tn "SnakeDailyReport" /fo LIST /v
pause
exit /b

:DELETE_TASK
echo.
schtasks /delete /tn "SnakeDailyReport" /f
if %errorlevel% equ 0 (
    echo [成功] 已刪除排程任務：SnakeDailyReport
) else (
    echo [失敗] 刪除失敗或該排程不存在。
)
pause
exit /b

:MENU_END
