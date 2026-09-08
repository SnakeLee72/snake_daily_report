# -*- coding: utf-8 -*-
"""
Snake Daily Report - GitHub 自動發布模組
將最新生成的 HTML 報表同步為 docs/index.html，並透過 Git 自動推送至 GitHub 倉庫，
搭配 GitHub Pages 即可實現日報自動上線、手機與電腦隨時在線閱讀。
"""

import subprocess
import shutil
from pathlib import Path

def publish_to_github(html_path: Path, branch: str = "main") -> bool:
    """
    將指定 HTML 報告發布至 GitHub
    """
    try:
        # 1. 將今日 HTML 同步複製至 docs/index.html 作為 GitHub Pages 首頁
        project_root = Path(__file__).parent
        docs_dir = project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        target_index = docs_dir / "index.html"
        shutil.copy(html_path, target_index)
        print(f"[GitHub 發布] 已更新 GitHub Pages 入口檔案：{target_index.name}")

        # 2. 檢查目前是否為 git 倉庫
        git_dir = project_root / ".git"
        if not git_dir.exists():
            print("[GitHub 發布提醒] 目前資料夾尚未初始化為 Git 倉庫。")
            print("請先在終端機中執行初始化與關聯指令（詳見說明）。")
            return False

        # 3. 檢查是否有設定遠端 origin
        remotes_proc = subprocess.run(
            ["git", "remote"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if not remotes_proc.stdout.strip() or "origin" not in remotes_proc.stdout:
            print("[GitHub 發布提醒] 尚未設定遠端倉庫 (remote origin)。")
            return False

        # 4. 執行 git add
        subprocess.run(["git", "add", "."], cwd=project_root, check=True)

        # 5. 檢查是否有變更需要 commit
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        if not status_proc.stdout.strip():
            print("[GitHub 發布] 檔案無任何變更，略過提交。")
            return True

        # 6. 建立 Commit
        date_str = html_path.stem
        commit_msg = f"Auto: Update Daily Report {date_str}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=project_root, check=True)
        print(f"[GitHub 發布] 建立 Commit: {commit_msg}")

        # 7. 推送至 GitHub
        print(f"[GitHub 發布] 正在推送至遠端倉庫 origin/{branch}...")
        push_proc = subprocess.run(
            ["git", "push", "origin", branch],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if push_proc.returncode == 0:
            print("[GitHub 發布成功] 每日報告已成功自動發布至 GitHub！")
            return True
        else:
            print(f"[GitHub 發布失敗] 推送時發生錯誤：\n{push_proc.stderr}")
            return False

    except Exception as e:
        print(f"[GitHub 發布異常] {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    today_str = datetime.now().strftime("%Y%m%d")
    sample_html = Path("reports") / f"{today_str}.html"
    if sample_html.exists():
        publish_to_github(sample_html)
    else:
        print(f"找不到測試檔案：{sample_html}")
