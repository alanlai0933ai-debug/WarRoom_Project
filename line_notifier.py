import requests
import database
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

# 🌟 新增：專門負責「產出戰報字串」的兵工廠
def get_briefing_message(period="今天"):
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    all_tasks = database.get_all_tasks()
    
    target_tasks = []
    
    for t in all_tasks:
        if t['status'] == '✅ 已完成': continue
            
        task_date = t['due_date']
        is_urgent = (t['is_urgent'] == 1)
        in_range = False
        
        if period == "今天":
            in_range = (task_date == today_str) or is_urgent
        elif period == "本週":
            end_of_week = (now + timedelta(days=6-now.weekday())).strftime('%Y-%m-%d')
            in_range = (today_str <= task_date <= end_of_week) or is_urgent
        elif period == "本月":
            current_month = now.strftime('%Y-%m')
            in_range = task_date.startswith(current_month) or is_urgent

        if in_range: target_tasks.append(t)

    # 產出最終字串並「回傳 (return)」
    if not target_tasks:
        return f"🎉 指揮官早安！{period}目前無急件或到期查核點，請依原定計畫推進！"
    else:
        msg = f"🔥 指揮官早安！{period}戰情摘要 ({today_str})\n"
        msg += "━" * 15 + "\n"
        for t in target_tasks:
            mark = "🚨" if t['is_urgent'] == 1 else "📅"
            msg += f"{mark} [{t['project_name'][:4]}] {t['title']}\n"
        msg += "\n🔗 請登入戰情室查看詳情或更新進度！"
        return msg

# 🌟 保留原本的發射台：專供早上 08:30 的排程器使用
def send_daily_briefing(period="今天"):
    # 呼叫兵工廠拿報告
    msg = get_briefing_message(period)
    
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
        print(f"✅ LINE {period}戰情報告 (Push) 發送成功！")
    else:
        print(f"❌ 發送失敗：{response.text}")