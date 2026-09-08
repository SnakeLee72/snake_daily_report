# -*- coding: utf-8 -*-
"""
Snake Daily Report - 匯出與郵件傳送模組 (Exporter)
提供加分功能：
1. PDF 匯出：使用 Windows 11 原生 Microsoft Edge Headless 模式渲染高品質 PDF
2. Email 寄送：透過 SMTP 發送 HTML 格式日報並支援 PDF 附件
"""
import os
import subprocess
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
from datetime import datetime

from config import SETTINGS, REPORTS_DIR

def export_html_to_pdf(html_path: Path, pdf_path: Path = None) -> Path:
    """
    調用 Windows 11 內建 Microsoft Edge Headless 模式將 HTML 轉換為 PDF
    """
    html_path = Path(html_path).resolve()
    if not pdf_path:
        pdf_path = html_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path).resolve()

    edge_exe = SETTINGS.get("EDGE_PATH", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    
    if not os.path.exists(edge_exe):
        # 嘗試尋找 64-bit 路徑
        alt_edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(alt_edge):
            edge_exe = alt_edge
        else:
            print(f"[PDF 匯出警告] 未找到 Microsoft Edge 執行檔：{edge_exe}，略過 PDF 產生")
            return None

    file_url = f"file:///{html_path.resolve().as_posix()}"
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={str(pdf_path)}",
        file_url
    ]

    try:
        print(f"[PDF 匯出] 正在使用 Edge 渲染 PDF：{pdf_path.name}...")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print(f"[PDF 匯出成功] 檔案已產生：{pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
            return pdf_path
        else:
            print(f"[PDF 匯出警告] 執行完畢但未偵測到 PDF 檔案")
            return None
    except Exception as e:
        print(f"[PDF 匯出異常]: {e}")
        return None

def send_email_report(html_path: Path, pdf_path: Path = None, subject: str = None) -> bool:
    """
    透過 Outlook 桌面用戶端發送每日報告郵件（含 HTML 內文與 PDF 附件）
    """
    try:
        import win32com.client
    except ImportError:
        print("[Email 錯誤] 缺少 win32com 模組，請確保安裝了 pywin32")
        return False

    receivers = SETTINGS.get("EMAIL_RECEIVERS", [])

    today_str = datetime.now().strftime("%Y-%m-%d")
    if not subject:
        subject = f"【Snake Daily Report】每日焦點情報日報 - {today_str}"

    html_path = Path(html_path)
    if not html_path.exists():
        print(f"[Email 錯誤] 找不到 HTML 報表檔案：{html_path}")
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    try:
        print("[Email] 正在呼叫 Outlook 用戶端準備信件...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        
        if receivers:
            mail.To = "; ".join(receivers)
        else:
            print("[Email 提示] 未設定收件者(SNAKE_EMAIL_RECEIVERS)，請在彈出的 Outlook 視窗自行填寫")

        mail.HTMLBody = html_content

        if pdf_path and Path(pdf_path).exists():
            mail.Attachments.Add(str(Path(pdf_path).resolve()))
            print(f"[Email] 已附加 PDF 檔案：{Path(pdf_path).name}")

        if receivers:
            mail.Send()
            print(f"[Email 發送成功] 日報已透過 Outlook 寄送至：{'; '.join(receivers)}")
        else:
            mail.Display()
            print("[Email 草稿已開啟] 請在 Outlook 視窗中確認並發送。")
            
        return True
    except Exception as e:
        print(f"[Email 呼叫 Outlook 異常]: {e}")
        return False

if __name__ == "__main__":
    today = datetime.now().strftime("%Y%m%d")
    sample_html = REPORTS_DIR / f"{today}.html"
    if sample_html.exists():
        pdf = export_html_to_pdf(sample_html)
        # 測試寄送（預設未配置帳密會優雅提示）
        send_email_report(sample_html, pdf)
    else:
        print(f"請先產生 HTML 檔案以進行測試：{sample_html}")
