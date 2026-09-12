# -*- coding: utf-8 -*-
"""
Snake Daily Report - 工作排程設定助手 (Python 版)
提供簡單直覺的指令式介面設定 Windows 每日工作排程，
跨版本相容，不受 CMD 編碼或換行符號影響。
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    python_exe = sys.executable
    task_name = "SnakeDailyReport"
    
    print("=" * 65)
    print("   Snake Daily Report - Windows 每日定時排程設定助手")
    print("=" * 65)
    print(f"\n[目前環境資訊]")
    print(f"- 專案路徑: {script_dir}")
    print(f"- Python  : {python_exe}\n")
    
    print("請選擇操作功能：")
    print("[1] 註冊/更新每日定時排程任務")
    print("[2] 查詢現有排程任務狀態")
    print("[3] 刪除此排程任務")
    print("[4] 立即執行一次日報主程式")
    print("[5] 離開")
    
    choice = input("\n請輸入選項 [1-5，預設 1]: ").strip()
    if not choice:
        choice = "1"
        
    if choice == "1":
        exec_time = input("請輸入每日自動執行時間 (格式 HH:mm，如 08:30): ").strip()
        if not exec_time:
            exec_time = "08:30"
            
        print("\n請選擇執行模式：")
        print("[1] Copilot 365 視窗自動化模式 (同聊天室連續 50 題)")
        print("[2] Direct 即時快速連網模式 (無介面秒級產出，最適合無人值守排程)")
        mode_choice = input("請輸入模式 [1 或 2，預設 1]: ").strip()
        mode = "copilot" if mode_choice != "2" else "direct"
        
        print("\n請輸入要收集的分類代碼 (A, B, C, D, E)，多個請用逗號隔開：")
        print("A: AI, B: New technology, C: 投資市場, D: 台灣股市, E: 美國股市")
        categories = input("直接按 Enter 則代表【全選】: ").strip().upper()
        
        email_choice = input("\n執行完畢後是否透過 Outlook 自動寄信給自己？ [y/N]: ").strip().lower()
        use_email = "--email" if email_choice == 'y' else ""
        cat_arg = f"--categories {categories}" if categories else ""
        
        main_script = script_dir / "main.py"
        run_cmd = f'"{python_exe}" "{main_script}" --mode {mode} {cat_arg} {use_email}'.strip()
        
        # 呼叫 schtasks 建立每日任務
        cmd = [
            "schtasks", "/create",
            "/tn", task_name,
            "/tr", run_cmd,
            "/sc", "DAILY",
            "/st", exec_time,
            "/f"
        ]
        
        print(f"\n正在向 Windows 註冊每日排程 [{task_name}]...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("=" * 65)
            print(" [成功] 每日工作排程已順利建立！")
            print(f" - 任務名稱: {task_name}")
            print(f" - 執行時間: 每天 {exec_time}")
            print(f" - 執行命令: {run_cmd}")
            print("=" * 65)
        else:
            print("\n [建立失敗] 系統回傳訊息：")
            print(res.stderr or res.stdout)
            print(">> 提示：若出現存取拒絕，請在批次檔上按右鍵選擇「以系統管理員身分執行」。")
            
    elif choice == "2":
        cmd = ["schtasks", "/query", "/tn", task_name, "/fo", "LIST", "/v"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout)
        else:
            print(f"[提示] 未查詢到名為 {task_name} 的排程任務。")
            
    elif choice == "3":
        cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f" [成功] 已刪除工作排程任務：{task_name}")
        else:
            print("[提示] 任務不存在或已刪除。")
            
    elif choice == "4":
        print("\n請選擇執行模式：")
        print("[1] Copilot 365 視窗自動化模式 (連續提問)")
        print("[2] Direct 即時快速連網模式 (免介面秒級產出，推薦)")
        mode_choice = input("請輸入模式 [1 或 2，預設 2]: ").strip()
        mode = "copilot" if mode_choice == "1" else "direct"

        print("\n請輸入要收集的分類代碼 (A, B, C, D, E)，多個請用逗號隔開：")
        print("A: AI, B: New technology, C: 投資市場, D: 台灣股市, E: 美國股市")
        categories = input("直接按 Enter 則代表【全選】: ").strip().upper()

        email_choice = input("\n執行完畢後是否透過 Outlook 自動寄信給自己？ [y/N]: ").strip().lower()

        run_args = [python_exe, str(script_dir / "main.py"), "--mode", mode]
        if categories:
            run_args.extend(["--categories", categories])
        if email_choice == 'y':
            run_args.append("--email")

        print(f"\n正在啟動 Snake Daily Report...")
        print(f"指令：{' '.join(run_args)}\n")
        subprocess.run(run_args)
    elif choice == "5":
        print("\n已退出程式。")
        return
        
    try:
        input("\n按 Enter 鍵結束程式...")
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == "__main__":
    main()
