@echo off
chcp 65001 >nul
title 關聯 GitHub 倉庫設定精靈

echo ============================================================
echo   🐍 Snake Daily Report - GitHub 倉庫關聯精靈
echo ============================================================
echo.
echo 請先在 GitHub 上建立一個新的公開 (Public) 或私有 (Private) 倉庫。
echo （建立時請「不要」勾選 Add a README, .gitignore 或 license）
echo.
set /p REPO_URL="請貼上您的 GitHub 倉庫網址 (例如 https://github.com/YourName/snake_daily_report.git): "

if "%REPO_URL%"=="" (
    echo [錯誤] 網址不能為空！
    pause
    exit /b
)

echo.
echo [1/3] 設定遠端倉庫 origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] 設定分支為 main...
git branch -M main

echo [3/3] 正在推送專案至 GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo  🎉 恭喜！專案已成功推送並關聯至 GitHub！
    echo ============================================================
    echo.
    echo 【開啟 GitHub Pages 線上網站教學】：
    echo  1. 前往您的 GitHub 倉庫頁面 -> 點擊上方 [Settings]
    echo  2. 在左側選單點擊 [Pages]
    echo  3. 在 Build and deployment 底下：
    echo     - Branch 選擇: [main]
    echo     - 資料夾選擇: [/docs]
    echo  4. 點擊 [Save] 儲存。
    echo.
    echo 幾分鐘後，您的線上日報網址就會啟用！
    echo 以後每天自動生成 HTML 後，程式都會自動更新並推送到 GitHub！
    echo ============================================================
) else (
    echo.
    echo [失敗] 推送時發生錯誤，請檢查網址或 GitHub 權限後重試。
)

echo.
pause
