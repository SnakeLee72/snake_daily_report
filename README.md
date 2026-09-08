# 🐍 Snake Daily Report - 每日焦點情報自動化系統

一套專為 **Windows 11 + Python 3.11/3.12** 設計的企業級每日情報自動化系統。  
每天自動收集 5 大類別共 50 則最新科技、產業、投資、開發與個人成長動態，經過資料去重、長度規範與 AI 智慧綜整後，產出具備現代科技風、深色主題的互動式 HTML Dashboard，並原生支援 Windows 11 Microsoft Edge PDF 匯出、SMTP 電子郵件自動發送與每日定時工作排程。

---

## 🌟 核心特色

1. **同聊天室連續 50 輪問答（Copilot 365 模式）**：
   - 沿用經嚴格驗證的 `WinSta0\default` Windows 桌面工作階段與視窗置頂技術。
   - **完全在同一個聊天視窗內**依序提問 50 個不同問題，無需反覆新開聊天室。
   - 自動透過 UIA 複製按鈕與剪貼簿解析【標題】、【摘要】（<=100字）、【來源】、【發布時間】、【原始連結】、【類別】。
   - 支援斷點續傳（每完成一筆立即寫入快取，中斷重啟不重抓）。
2. **雙引擎彈性架構**：
   - **Copilot 模式 (`--mode copilot`)**：深入與 Microsoft 365 Copilot 互動問答。
   - **Direct 模式 (`--mode direct`)**：即時網路快速檢索（標準庫 RSS 解析），適合排程在螢幕鎖定/無介面環境下無人值守秒級產出。
3. **資料去重與合規過濾**：
   - 自動過濾重複連結與文字重疊率 >65% 之同類新聞，確保同類重大事件只保留一則。
   - 嚴格控制每則摘要在 100 字以內。
4. **AI 智能多維度摘要**：
   - 自動生成：**今日三大重點**、**今日投資觀察**、**今日產業觀察**、**今日AI觀察**、**今日一句總結**。
   - 可隨時替換外部 LLM API（支援 Gemini API / OpenAI API），亦內建專業規則分析引擎，保證離線無金鑰時依然能精準綜整。
5. **現代科技風深色 HTML Dashboard (`reports/YYYYMMDD.html`)**：
   - 深夜藍色調 (`#0a0f1d`) 搭配半透明毛玻璃質感與霓虹漸層光暈。
   - **即時關鍵字搜尋**：邊打字邊即時過濾所有新聞卡片。
   - **分類標籤快篩與折疊**：支援單類別過濾、一鍵全展開/全收合。
   - **資訊分類統計儀表板**：顯示 5 大類別收錄篇數與狀態。
   - **今日重點 TOP 10**：首頁焦點卡片，直觀呈現當日最核心事件。
   - **直覺互動**：每則資訊皆附「點擊開啟原文 ↗」與獨立來源/時間標籤。
6. **加分功能完整內建**：
   - **PDF 匯出**：調用 Windows 11 內建 Microsoft Edge Headless 模式，一鍵將 HTML 轉為高品質 PDF。
   - **Email 自動發送**：標準庫 SMTP 支援，日報內嵌於信件內文，並自動附加 PDF 檔案。
   - **Windows 11 工作排程**：內建 `create_task.bat`，管理員身分一鍵註冊每日定時執行任務。

---

## 📋 50 則主題收錄清單

系統每日依序追蹤以下 5 大領域共 50 則核心標的：

| 分類 | 數量 | 涵蓋主題清單 |
| :--- | :---: | :--- |
| **A. AI與科技** | 10 | 1. OpenAI, 2. ChatGPT, 3. Gemini, 4. Claude, 5. Microsoft Copilot, 6. Google AI, 7. NVIDIA, 8. AMD, 9. Intel, 10. Apple |
| **B. Notebook/ODM產業** | 10 | 1. Lenovo, 2. HP, 3. Dell, 4. ASUS, 5. Acer, 6. Compal, 7. Quanta, 8. Wistron, 9. Inventec, 10. Camera Module產業 |
| **C. 投資市場** | 15 | 1. 台股加權指數, 2. 美股四大指數, 3. 台積電, 4. 特斯拉, 5. 亞馬遜, 6. Google, 7. Meta, 8. Broadcom, 9. Oracle, 10. 三大法人, 11. 外資買賣超, 12. 美元指數, 13. 台幣匯率, 14. 黃金, 15. 美國利率相關資訊 |
| **D. 開發技術** | 10 | 1. Python, 2. FastAPI, 3. Streamlit, 4. PyInstaller, 5. Godot Engine, 6. AI Agent, 7. Claude Code, 8. Codex, 9. Gemini CLI, 10. VS Code |
| **E. 個人成長** | 5 | 1. 健康研究, 2. 長壽研究, 3. 心理學, 4. 商業思維, 5. 商用英文 |

---

## 📂 專案檔案架構

```
d:\Antigravity\Sanguo\snake_daily_report\
├── config.py                 # 50 個主題結構清單、Copilot 提問樣板、路徑與環境變數設定
├── copilot_collector.py      # Copilot 365 視窗自動化收集核心（同一聊天室連續50問）
├── direct_collector.py       # 輕量即時連網檢索備援模組（RSS/無介面）
├── summarizer.py             # AI 摘要核心（支援 Gemini/OpenAI API 或內建智慧綜整）
├── report_generator.py       # 現代科技風深色 HTML Dashboard 渲染器
├── exporter.py               # Edge Headless PDF 匯出與 SMTP 電子郵件自動發送
├── main.py                   # 專案統一執行主程式（含命令列參數與流程調度）
├── create_task.bat           # Windows 11 排程設定精靈（一鍵建立每日自動執行）
├── requirements.txt          # Python 相依套件清單
├── README.md                 # 專案詳細繁體中文說明文件
├── data/                     # 存放每日暫存 raw_data_YYYYMMDD.json
└── reports/                  # 存放產出的 YYYYMMDD.html 與 YYYYMMDD.pdf
```

---

## 🚀 快速安裝與環境準備

### 1. 安裝環境需求
- **作業系統**：Windows 11 / Windows 10
- **Python 版本**：Python 3.11 或 Python 3.12
- **瀏覽器**：Windows 11 內建 Microsoft Edge（供 PDF 自動轉檔）

### 2. 安裝 Python 相依套件
在終端機中切換至專案目錄並執行：
```powershell
cd d:\Antigravity\Sanguo\snake_daily_report
pip install -r requirements.txt
```

---

## 💻 執行方式說明

### 1. 預設模式（Copilot 365 自動化提問）
請先開啟並登入 **Microsoft 365 Copilot** 應用程式，然後在終端機執行：
```powershell
python main.py --mode copilot
```
> **說明**：程式會自動置頂 Copilot 視窗，並在同一個聊天室中連續提出 50 題問題，逐題抓取回覆，最後產出 `reports/YYYYMMDD.html` 與 `reports/YYYYMMDD.pdf`。

### 2. 即時連網備援模式（Direct 模式）
若未開啟 Copilot 365、欲快速測試，或在電腦螢幕鎖定/無介面環境下由排程無人值守執行：
```powershell
python main.py --mode direct
```
> **說明**：約 15~20 秒內即可檢索完 50 則主題最新資訊並完成 HTML / PDF 報表產出。

### 3. 開發與快速測試參數
```powershell
# 僅測試前 5 題：
python main.py --mode direct --limit 5

# 僅讀取今日已抓好的快取重新生成報表：
python main.py --mode cache

# 產生報告時同步發送 Email：
python main.py --mode direct --email

# 不產生 PDF 檔案（僅產生 HTML）：
python main.py --mode direct --no-pdf
```

---

## ⚙️ 進階設定（可選）

可於 `config.py` 或設定系統環境變數：

### 1. LLM API 設定（若欲使用外部 AI 生成摘要）
- `GEMINI_API_KEY`：Google Gemini API 金鑰
- `OPENAI_API_KEY`：OpenAI API 金鑰
> *若未設定，系統將自動啟用內建之專業多維度綜整引擎，無需金鑰即可產生流暢專業的分析報告。*

### 2. Email SMTP 設定（若欲啟用 `--email` 自動寄信）
- `SNAKE_SMTP_SERVER`：預設 `smtp.gmail.com`
- `SNAKE_SMTP_PORT`：預設 `587`
- `SNAKE_SMTP_USER`：您的發信郵箱
- `SNAKE_SMTP_PASS`：應用程式專用密碼（App Password）
- `SNAKE_EMAIL_RECEIVERS`：收件者清單（多個以逗號 `,` 隔開）

---

## ⏰ Windows 11 工作排程設定 (兩種方式皆可)

專案提供兩種簡單直覺的排程設定方式：

### 方式一：使用批次檔 (create_task.bat)
1. 前往 `d:\Antigravity\Sanguo\snake_daily_report\`。
2. 對 `create_task.bat` 點擊右鍵，選擇 **「以系統管理員身分執行」**。
3. 依照選單輸入每日執行時間（預設 `08:30`）與模式，即可自動註冊進 Windows 工作排程器。

### 方式二：使用 Python 設定助手 (setup_task.py)
若習慣在終端機中操作：
```powershell
python setup_task.py
```
依照畫面提示輸入時間與模式即可完成排程建立，跨平台且不受命令提示字元編碼干擾。

---

## 📊 報表檢視

每日報表儲存於 `reports/` 目錄：
- **HTML Dashboard**：直接以任何現代瀏覽器（Edge / Chrome / Brave）雙擊開啟即可體驗現代科技風介面、即時搜尋、分類篩選與點擊前往原文。
- **PDF 報告**：已由 Edge 引擎渲染完畢，可直接用於列印、歸檔或行動裝置閱讀。
