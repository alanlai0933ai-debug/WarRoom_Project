import sqlite3
import os

# 🌟 雲端智慧路徑：確保在 Fly.io 掛載的 /data 下運作
DB_PATH = '/data/war_room.db' if os.path.exists('/data') else 'war_room.db'
DB_FILE = DB_PATH

def get_db_connection():
    """建立具備高穩定性的連線引擎"""
    # 🌟 增加 timeout=10：防止雲端硬碟讀寫較慢時發生 'database is locked' 錯誤
    conn = sqlite3.connect(DB_FILE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """初始化大腦：一次到位，包含所有擴充欄位"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🌟 開啟 WAL 模式：解決多人同時寫入資料時的衝突問題
    cursor.execute('PRAGMA journal_mode=WAL;')
    
    # 🌟 建立資料表 (一次性包含所有最新欄位，避免部署後報錯)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            title TEXT NOT NULL,
            tag TEXT,
            owner TEXT,
            due_date TEXT,
            status TEXT DEFAULT '📋 待辦事項',
            detailed_status TEXT,
            vendor_and_notes TEXT,
            is_urgent INTEGER DEFAULT 0,
            parent_id INTEGER,
            weight INTEGER DEFAULT 1,
            target_total INTEGER DEFAULT 1,
            current_progress INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 戰略室大腦 ({DB_FILE}) 已就緒，WAL 模式已啟動！")

def upgrade_db_schema():
    """資料庫無痛升級手術：新增年度與階層權重欄位"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🌟 在清單中加入 "year"
    cols = ["parent_id", "weight", "target_total", "current_progress", "year"]
    
    for col in cols:
        try:
            # 💡 針對不同欄位設定合理的預設值
            if col == "year":
                default = "DEFAULT 115"  # 預設為 115 年度 (可依需求改為 2026)
            elif "progress" in col or "urgent" in col:
                default = "DEFAULT 0"
            else:
                default = "DEFAULT 1"
                
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {default}")
            print(f"✅ 成功補齊欄位：{col}")
        except sqlite3.OperationalError:
            # 欄位如果已經存在，SQLite 會報錯，我們直接跳過即可
            continue 
            
    conn.commit()
    conn.close()
    print("✨ 資料庫結構已自動校準至最新版本。")

# --- 核心寫入與讀取功能 (已全面串接 get_db_connection) ---

def add_task(project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id=None, weight=1, target_total=1, current_progress=0, year=115):
    conn = get_db_connection()
    cursor = conn.cursor()
    # 🌟 SQL 語法要有 year，VALUES 要有對應的 ?，並在最後傳入 year 變數
    cursor.execute('''
        INSERT INTO tasks (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id, weight, target_total, current_progress, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_name, title, tag, owner, due_date, status, detailed_status, vendor_and_notes, is_urgent, parent_id, weight, target_total, current_progress, year))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_task_status(task_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()

def update_task_details(task_id, detailed_status, vendor_notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET detailed_status = ?, vendor_and_notes = ? WHERE id = ?', (detailed_status, vendor_notes, task_id))
    conn.commit()
    conn.close()

def update_task_full(task_id, title, project_name, tag, owner, due_date, weight, target_total, is_urgent, detailed_status, vendor_and_notes):
    conn = get_db_connection()
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

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def update_task_progress(task_id, new_progress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET current_progress = ? WHERE id = ?', (new_progress, task_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    upgrade_db_schema()