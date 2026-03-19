from nicegui import ui

# ==========================================
# 🎨 頂部導覽列 (SaaS 風格 Header)
# ==========================================
with ui.header(elevated=True).style('background-color: #1e293b'):
    ui.icon('space_dashboard', size='md').classes('text-white')
    ui.label('雙專案戰略指揮中心').classes('text-2xl font-bold text-white ml-4')

# ==========================================
# 🏠 主畫面容器 (置中排版)
# ==========================================
with ui.column().classes('w-full items-center mt-12'):
    
    # 建立一個帶有陰影與圓角的漂亮卡片
    with ui.card().classes('w-11/12 max-w-4xl shadow-xl p-8 rounded-2xl'):
        ui.label('👋 歡迎登入！戰略基地已成功啟動。').classes('text-3xl font-extrabold text-blue-800 mb-2')
        ui.label('系統環境一切正常。我們即將在這裡建立「專案 A」與「專案 B」的任務看板與數據儀表板。').classes('text-lg text-gray-600')
        
        ui.separator().classes('my-4')
        
        # 測試一個互動按鈕
        ui.button('點擊測試系統連線', 
                  on_click=lambda: ui.notify('連線成功！準備進入下一步！', type='positive', position='top-right')
                 ).props('rounded color="primary" icon="check_circle"')

# ==========================================
# 🚀 啟動伺服器
# ==========================================
ui.run(title='戰略指揮中心', favicon='🔥')