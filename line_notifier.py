import requests
import database
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # 🌟 自動讀取 .env 檔案
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_daily_briefing():

    # 2. 啟動大腦，撈取「今日急件」與「今日到期」的查核點
    today_str = datetime.now().strftime('%Y-%m-%d')
    all_tasks = database.get_all_tasks()
    
    # 過濾條件：未完成，且 (日期是今天 或 標記為急件)
    today_tasks = [
        t for t in all_tasks 
        if t['status'] != '✅ 已完成' and (t['due_date'] == today_str or t['is_urgent'] == 1)
    ]

    # 3. 撰寫戰情報告字串
    if not today_tasks:
        msg = "🎉 指揮官早安！今日目前無急件或到期查核點，請依原定計畫推進！"
    else:
        msg = f"🔥 指揮官早安！今日戰情摘要 ({today_str})\n"
        msg += "━" * 15 + "\n"
        for t in today_tasks:
            # 用 Emoji 區分急件或一般到期
            mark = "🚨" if t['is_urgent'] == 1 else "📅"
            # 濃縮顯示：[專案名] 任務標題
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
        print("✅ LINE 戰情報告發送成功！")
    else:
        print(f"❌ 發送失敗：{response.text}")

# 測試執行
if __name__ == '__main__':
    send_daily_briefing()