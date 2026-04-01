import requests
import database
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv() # 🌟 自動讀取 .env 檔案
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

# 🌟 1. 加入 period 參數，預設為「今天」
def send_daily_briefing(period="今天"):
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    all_tasks = database.get_all_tasks()
    
    target_tasks = []
    
    # 🌟 2. 啟動時間過濾引擎
    for t in all_tasks:
        if t['status'] == '✅ 已完成':
            continue  # 完成的任務直接跳過不報
            
        task_date = t['due_date']
        is_urgent = (t['is_urgent'] == 1)
        
        in_range = False
        
        # 根據指令判斷是否在時間範圍內 (急件永遠優先顯示)
        if period == "今天":
            in_range = (task_date == today_str) or is_urgent
            
        elif period == "本週":
            # 計算出本週日 (7天內的邊界)
            end_of_week = (now + timedelta(days=6-now.weekday())).strftime('%Y-%m-%d')
            in_range = (today_str <= task_date <= end_of_week) or is_urgent
            
        elif period == "本月":
            # 直接比對年與月 (例如 '2026-04')
            current_month = now.strftime('%Y-%m')
            in_range = task_date.startswith(current_month) or is_urgent

        # 符合條件的就加入戰報清單
        if in_range:
            target_tasks.append(t)

    # 3. 撰寫動態戰情報告字串
    if not target_tasks:
        msg = f"🎉 指揮官早安！{period}目前無急件或到期查核點，請依原定計畫推進！"
    else:
        msg = f"🔥 指揮官早安！{period}戰情摘要 ({today_str})\n"
        msg += "━" * 15 + "\n"
        for t in target_tasks:
            # 保留您原本極佳的 UX 設計！
            mark = "🚨" if t['is_urgent'] == 1 else "📅"
            msg += f"{mark} [{t['project_name'][:4]}] {t['title']}\n"
            
        msg += "\n🔗 請登入戰情室查看詳情或更新進度！"

    # 4. 呼叫 LINE 飛彈發射！
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'to': USER_ID,
        'messages': [{'type': 'text', 'text': msg}]
    }
    
    response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"✅ LINE {period}戰情報告發送成功！")
    else:
        print(f"❌ 發送失敗：{response.text}")

# 本地測試執行
if __name__ == '__main__':
    send_daily_briefing("本週") # 您可以改成 "今天" 或 "本月" 測試看看