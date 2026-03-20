import sqlite3
import os

# 🌟 雲端智慧路徑：如果在 Fly.io 雲端有掛載 /data 硬碟，就存在那裡，否則存本地
DB_PATH = '/data/war_room.db' if os.path.exists('/data') else 'war_room.db'
DB_FILE = DB_PATH

def init_db():
# ... (底下維持不變) ...
    """初始化資料庫與資料表 (大腦開機)"""
    # 建立連線 (如果檔案不存在，SQLite 會自動幫你建立一個新的)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 🌟 升級：開啟 WAL 模式 (Write-Ahead Logging)，大幅提升多人同時操作的效能與穩定性！
    cursor.execute('PRAGMA journal_mode=WAL;')
    
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

def add_task(project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id=None, weight=1, target_total=1, current_progress=0):
    """將新任務寫入大腦 (支援大包小與權重)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # SQL 語法也升級了，加入了新的 4 個欄位
    cursor.execute('''
        INSERT INTO tasks (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id, weight, target_total, current_progress)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id, weight, target_total, current_progress))
    
    conn.commit()
    conn.close()
    print(f"✅ 任務「{title}」已成功寫入！(權重:{weight}, 目標:{target_total})")

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

def update_task_progress(task_id, new_progress):
    """更新大腦中指定任務的目標達成進度"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET current_progress = ? WHERE id = ?', (new_progress, task_id))
    conn.commit()
    conn.close()
    print(f"📈 任務 ID {task_id} 進度已更新為：{new_progress}")

def upgrade_db_schema():
    """資料庫無痛升級手術：加入大包小、權重與進度欄位"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 使用 try-except 來防呆，如果欄位已經加過了就不會報錯
    try:
        # 1. 紀錄「我的爸爸是誰」(NULL 代表自己就是大任務)
        cursor.execute("ALTER TABLE tasks ADD COLUMN parent_id INTEGER")
        # 2. 紀錄這張卡的權重 (預設為 1)
        cursor.execute("ALTER TABLE tasks ADD COLUMN weight INTEGER DEFAULT 1")
        # 3. 紀錄總目標數 (例如 10 份報告)
        cursor.execute("ALTER TABLE tasks ADD COLUMN target_total INTEGER DEFAULT 1")
        # 4. 紀錄目前進度 (例如已完成 1 份)
        cursor.execute("ALTER TABLE tasks ADD COLUMN current_progress INTEGER DEFAULT 0")
        
        print("🚀 資料庫擴充手術成功！已具備【大包小】與【權重進度】運算能力！")
    except sqlite3.OperationalError:
        print("✨ 資料庫已經升級過了，大腦頭好壯壯！")
        
    conn.commit()
    conn.close()

# ==========================================
# 🚀 單獨執行這個檔案時，啟動建置與升級程序
# ==========================================
if __name__ == '__main__':
    print("🧠 準備啟動大腦建置與升級程序...")
    init_db()
    upgrade_db_schema() # 🌟 執行升級手術

# ==========================================
# 🌟 最終兵器：全範圍情報更新引擎
# ==========================================
def update_task_full(task_id, title, project_name, tag, owner, due_date, weight, target_total, is_urgent, detailed_status, vendor_and_notes):
    # 🌟 修正 1：移除多餘的 import sqlite3
    # 🌟 修正 2：改用統一的 DB_FILE 變數，避免未來改檔名時這裡報錯
    conn = sqlite3.connect(DB_FILE) 
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET title=?, project_name=?, tag=?, owner=?, due_date=?, 
            weight=?, target_total=?, is_urgent=?, 
            detailed_status=?, vendor_and_notes=?
        WHERE id=?
    ''', (title, project_name, tag, owner, due_date, weight, target_total, is_urgent, detailed_status, vendor_and_notes, task_id))
    
    conn.commit()
    conn.close()  
    