from nicegui import ui
# ==========================================
# 🧠 系統大腦：動態專案清單
# (未來這裡會改成從 SQLite 資料庫自動讀取！)
# ==========================================
PROJECT_LIST = [
    '🌊 專案 A (海岸清理)',
    '🏛️ 專案 B (標案企劃)',
    '🌱 專案 C (臨時交辦事項)' # 💡 你隨時可以在這裡新增或修改，不用動到下面的 UI 程式碼
]

# ==========================================
# 🛠️ 模組化工具：生產「高階任務卡片」的機器
# 支援勾選框、超連結、急件標示
# ==========================================
def create_rich_card(task_name, tag, is_urgent=False, doc_url=None):
    with ui.card().classes('w-full mb-3 cursor-pointer hover:shadow-lg transition-all border-l-4 ' + ('border-red-500' if is_urgent else 'border-blue-500')):
        with ui.row().classes('w-full justify-between items-start no-wrap'):
            # 左側：勾選框與任務名稱
            ui.checkbox(task_name).classes('font-bold text-gray-800 text-md')
            
            # 右側：雲端硬碟超連結 (如果有提供 URL 的話)
            if doc_url:
                with ui.link(target=doc_url, new_tab=True):
                    ui.button(icon='folder_open', color='primary').props('flat dense').tooltip('開啟相關雲端文件')

        # 底部標籤區
        with ui.row().classes('w-full justify-between items-center mt-1 pl-8'):
            ui.label(tag).classes('text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md')
            if is_urgent:
                ui.label('🔥 今日急件').classes('text-xs text-red-600 font-bold bg-red-100 px-2 py-1 rounded-md')

# ==========================================
# 🆕 隱藏的「新增任務」彈出視窗 (Dialog)
# ==========================================
with ui.dialog() as new_task_dialog, ui.card().classes('w-96 p-6 rounded-2xl shadow-2xl'):
    ui.label('✨ 新增戰略任務').classes('text-xl font-extrabold text-blue-900 mb-4')
    
    # 輸入表單
    task_name = ui.input('任務名稱 / 查核點').classes('w-full mb-2')
    project_select = ui.select(PROJECT_LIST, label='所屬專案').classes('w-full mb-2')    
    tag_select = ui.select(['行政作業', '數據處理', '現場會勘', '廠商協調', '其他'], label='任務標籤').classes('w-full mb-2')
    is_urgent = ui.checkbox('🔥 標記為今日急件').classes('mt-2 text-red-600 font-bold')
    
    ui.separator().classes('my-4')
    
    # 底部按鈕
    with ui.row().classes('w-full justify-end gap-2'):
        ui.button('取消', on_click=new_task_dialog.close, color='gray').props('flat')
        
        # 💡 這個儲存按鈕，未來會綁定我們寫的 SQLite 資料庫儲存功能！
        ui.button('💾 儲存任務', on_click=lambda: [
            ui.notify(f'準備將「{task_name.value}」存入資料庫！', type='positive'),
            new_task_dialog.close()
        ]).props('rounded')

# ==========================================
# 🎨 頂部導覽列 (加入「➕ 新增任務」按鈕)
# ==========================================
with ui.header(elevated=True).style('background-color: #0f172a').classes('items-center justify-between px-6'):
    with ui.row().classes('items-center'):
        ui.icon('query_stats', size='md').classes('text-white')
        ui.label('專案戰略指揮中心').classes('text-2xl font-bold text-white ml-2')
    
    # 🌟 點擊這個按鈕，就會呼叫上面的對話框彈出來！
    ui.button('➕ 新增任務', on_click=new_task_dialog.open, color='blue-500').classes('font-bold shadow-md')

# ==========================================
# 📊 區塊 4：全局大進度條 (首頁最上方)
# ==========================================
with ui.row().classes('w-full max-w-7xl mx-auto mt-6 px-4 gap-6'):
    with ui.card().classes('w-full bg-white shadow-md rounded-xl p-6'):
        ui.label('🏆 專案全局查核點進度').classes('text-lg font-extrabold text-gray-800 mb-4')
        with ui.row().classes('w-full items-center gap-4'):
            # 專案 A 進度
            with ui.column().classes('w-[48%]'):
                with ui.row().classes('w-full justify-between items-end mb-1'):
                    ui.label('🌊 專案 A：海岸清理計畫').classes('font-bold text-blue-800')
                    ui.label('45% (已過 2/5 查核點)').classes('text-sm text-gray-500')
                ui.linear_progress(value=0.45, show_value=False).props('color="blue" size="12px rounded"')
            
            # 專案 B 進度
            with ui.column().classes('w-[48%]'):
                with ui.row().classes('w-full justify-between items-end mb-1'):
                    ui.label('🏛️ 專案 B：環保局年度標案').classes('font-bold text-purple-800')
                    ui.label('12% (已過 1/8 查核點)').classes('text-sm text-gray-500')
                ui.linear_progress(value=0.12, show_value=False).props('color="purple" size="12px rounded"')

# ==========================================
# 🏠 主體排版：左側 (時間/重點) vs 右側 (看板)
# ==========================================
with ui.row().classes('w-full max-w-7xl mx-auto mt-6 px-4 gap-6 no-wrap items-start'):
    
    # -----------------------------------
    # 左側面板 (佔比約 30%)
    # -----------------------------------
    with ui.column().classes('w-1/3 min-w-[320px] gap-6'):
        
        # 區塊 3：今日重點工作區
        with ui.card().classes('w-full bg-red-50 border border-red-100 shadow-md'):
            ui.label('🚨 今日必須擊破 (Focus)').classes('text-lg font-extrabold text-red-800 mb-2')
            create_rich_card('回覆環保署預算執行疑義', '行政作業', is_urgent=True)
            create_rich_card('聯絡清運廠商確認報價', '廠商協調', is_urgent=True)

        # 區塊 2：月曆區 (顯示查核點)
        with ui.card().classes('w-full shadow-md'):
            ui.label('📅 本月查核點 (Milestones)').classes('text-lg font-extrabold text-gray-800 mb-2')
            # 放入一個可互動的月曆元件
            ui.date(value='2026-03-19').classes('w-full shadow-none')
            ui.separator().classes('my-2')
            # 月曆下方的重大節點提示
            with ui.row().classes('w-full items-center gap-2 mb-1'):
                ui.icon('flag', color='blue')
                ui.label('3/25 - 專案A：繳交期中報告').classes('text-sm font-bold text-gray-700')
            with ui.row().classes('w-full items-center gap-2'):
                ui.icon('flag', color='purple')
                ui.label('3/30 - 專案B：投標截止日').classes('text-sm font-bold text-gray-700')

    # -----------------------------------
    # 右側面板 (佔比約 70%)
    # -----------------------------------
    with ui.column().classes('flex-grow w-2/3'):
        
        # 區塊 1 & 5：待辦事項看板區 (加入動態 Tabs)
        with ui.card().classes('w-full shadow-md p-0'):
            
            # 準備一個空字典，用來記住每一個被創造出來的標籤物件
            tab_objects = {}
            
            # 1. 動態生成標籤導覽列
            with ui.tabs().classes('w-full bg-slate-100 text-gray-700 font-bold') as tabs:
                for proj_name in PROJECT_LIST:
                    # 依據清單，自動建立標籤並存起來
                    tab_objects[proj_name] = ui.tab(proj_name) 
                    
                # 手動加上固定不變的歷史成就庫
                tab_archive = ui.tab('🗄️ 歷史成就庫 (Archive)')

            # 2. 動態生成標籤對應的看板內容
            # 預設顯示清單中的第一個專案
            with ui.tab_panels(tabs, value=tab_objects[PROJECT_LIST[0]]).classes('w-full bg-transparent p-4'):
                
                # 利用 for 迴圈，幫「每一個專案」自動畫出專屬的看板！
                for proj_name in PROJECT_LIST:
                    with ui.tab_panel(tab_objects[proj_name]):
                        with ui.row().classes('w-full items-start gap-4 no-wrap overflow-x-auto'):
                            
                            # 待辦直欄
                            with ui.column().classes('w-1/2 bg-slate-50 p-4 rounded-xl'):
                                ui.label('📋 執行中事項').classes('font-bold text-gray-700 mb-2')
                                # 💡 顧問提示：因為還沒接資料庫，我們先放一張通用的卡片佔位子
                                create_rich_card(f'這是 {proj_name} 的待辦任務', '系統測試')
                            
                            # 阻礙/等待直欄
                            with ui.column().classes('w-1/2 bg-orange-50 p-4 rounded-xl'):
                                ui.label('🛑 等待外部回覆 (Blocked)').classes('font-bold text-orange-800 mb-2')

                # 🌟 保留你原本完美的：歷史成就庫專屬面板
                with ui.tab_panel(tab_archive):
                    with ui.row().classes('w-full justify-between items-center mb-4'):
                        ui.label('🏆 專案歷史結算紀錄').classes('text-lg font-bold text-gray-800')
                        ui.button('📥 匯出 Excel 月報表', color='green').props('rounded outline icon="download"')

                    columns = [
                        {'name': 'date', 'label': '完成日期', 'field': 'date', 'sortable': True, 'align': 'left'},
                        {'name': 'project', 'label': '所屬專案', 'field': 'project', 'sortable': True, 'align': 'left'},
                        {'name': 'task', 'label': '任務名稱 / 查核點', 'field': 'task', 'align': 'left'},
                        {'name': 'tag', 'label': '任務標籤', 'field': 'tag', 'align': 'center'},
                    ]
                    rows = [
                        {'date': '2026-03-15', 'project': '專案 A', 'task': '完成第一季經費初核', 'tag': '行政流程'},
                        {'date': '2026-03-12', 'project': '專案 A', 'task': '建立海岸空拍圖座標', 'tag': '數據處理'},
                        {'date': '2026-03-10', 'project': '專案 B', 'task': '遞交投標意向書', 'tag': '企劃前置'},
                    ]
                    ui.table(columns=columns, rows=rows, row_key='task').classes('w-full')                   

# ==========================================
ui.run(title='戰略指揮中心', favicon='🔥')