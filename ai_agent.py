import os
import google.generativeai as genai
import database
from dotenv import load_dotenv

load_dotenv()
# 🌟 初始化 Gemini 武器庫
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(user_query):
    # 1. 撈取情報：從資料庫拿出所有「未完成」的任務
    all_tasks = database.get_all_tasks()
    pending_tasks = [t for t in all_tasks if t['status'] != '✅ 已完成']
    
    # 2. 整理情報：轉換成 AI 看得懂的條列式清單
    db_context = "目前的未完成任務清單如下：\n"
    for t in pending_tasks:
        db_context += f"- 專案：{t['project_name']}, 任務：{t['title']}, 期限：{t['due_date']}, 急件：{'是' if t['is_urgent']==1 else '否'}\n"
        
    # 3. 下達人設指令 (System Prompt)：賦予它軍事幕僚的靈魂
    prompt = f"""
    你是一位軍事風格的頂級 AI 戰情幕僚。你的長官（指揮官）正在用 LINE 向你詢問專案進度。
    請根據以下提供的「任務清單」事實，來回答指揮官的問題。
    
    【嚴格規範】
    1. 必須以「報告指揮官！」作為開頭。
    2. 語氣必須精簡、重點明確、態度專業。
    3. 如果問題超出清單範圍，請誠實回報「目前情報庫中沒有相關數據」。
    4. 請適當使用 Emoji 讓排版更易讀。
    
    【背景情報庫】
    {db_context}
    
    【指揮官提問】
    {user_query}
    """
    
    # 4. 呼叫最新的 Gemini 1.5 Flash 模型進行高速推論
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ 報告指揮官，AI 通訊模組遭遇干擾：{str(e)}"