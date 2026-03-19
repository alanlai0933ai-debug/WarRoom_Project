import sqlite3

# 定義資料庫檔案名稱 (它會自動產生在你的資料夾裡)
DB_FILE = 'war_room.db'

def init_db():
    """初始化資料庫與資料表 (大腦開機)"""
    # 建立連線 (如果檔案不存在，SQLite 會自動幫你建立一個新的)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 🌟 根據團隊黃金需求，建立超強大的 tasks 資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 任務的身分證號碼 (自動遞增)
            project_name TEXT NOT NULL,            -- 所屬專案
            title TEXT NOT NULL,                   -- 任務名稱 / 查核點
            tag TEXT,                              -- 任務標籤 (活動辦理、行政作業...)
            owner TEXT,                            -- 👤 主責人員
            due_date TEXT,                         -- 📅 預計完成時間
            status TEXT DEFAULT '📋 待辦事項',       -- 看板狀態 (待辦/進行中/卡關/已完成)
            detailed_status TEXT,                  -- 🔍 細部狀態 (規劃中/待追蹤/執行中)
            vendor_and_notes TEXT,                 -- 🏢 廠商資訊與追蹤日誌
            is_urgent INTEGER DEFAULT 0            -- 🔥 是否為今日急件 (0=否, 1=是)
        )
    ''')
    
    # 儲存變更並關閉連線
    conn.commit()
    conn.close()
    print(f"✅ 戰略室大腦 ({DB_FILE}) 與任務記憶區已成功建立！")

def add_task(project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent):
    """(預先準備) 新增任務的工具"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 把收到的資料安全地塞進大腦裡
    cursor.execute('''
        INSERT INTO tasks (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent))
    
    conn.commit()
    conn.close()
    print(f"💾 成功將任務「{title}」寫入資料庫！")

def get_all_tasks():
    """從大腦撈出所有任務，並轉換成好用的字典格式"""
    conn = sqlite3.connect(DB_FILE)
    # 🌟 加上這行，讓撈出來的資料變成 Dictionary，我們前端才好用 key 去呼叫
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]

def update_task_status(task_id, new_status):
    """更新大腦中指定任務的狀態"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 使用 UPDATE 語法，精準瞄準那一張卡片的 ID 進行修改
    cursor.execute('''
        UPDATE tasks 
        SET status = ? 
        WHERE id = ?
    ''', (new_status, task_id))
    
    conn.commit()
    conn.close()
    print(f"🔄 任務 ID {task_id} 的狀態已成功更新為：{new_status}")

def update_task_details(task_id, detailed_status, vendor_notes):
    """更新大腦中指定任務的「細部狀態」與「廠商日誌」"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET detailed_status = ?, vendor_and_notes = ? 
        WHERE id = ?
    ''', (detailed_status, vendor_notes, task_id))
    
    conn.commit()
    conn.close()
    print(f"📝 任務 ID {task_id} 的細節情報已更新！")

def delete_task(task_id):
    """從大腦中徹底刪除指定任務"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 執行 SQL 刪除指令
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()
    print(f"🗑️ 任務 ID {task_id} 已徹底刪除！")

# ==========================================
# 🚀 單獨執行這個檔案時，啟動建置程序
# ==========================================
if __name__ == '__main__':
    print("🧠 準備啟動大腦建置程序...")
    init_db()
    