from nicegui import ui
import database
import calendar        # 🌟 新增：Python 內建的超強月曆計算機
from datetime import datetime # 🌟 新增：用來取得現在是幾月
from nicegui import ui
import database

# ==========================================
# 🧠 系統大腦：動態專案清單
# ==========================================
PROJECT_LIST = [
    '🌊 專案 A (海岸清理)',
    '🏛️ 專案 B (標案企劃)',
    '🌱 專案 C (臨時交辦事項)'
]

# ==========================================
# 🛠️ 模組化工具：共用的「唯一情報詳細視窗」
# ==========================================
def open_task_detail_modal(t):
    # 防呆：如果是假資料就不打開
    if t.get('id', -1) < 0:
        ui.notify('這是示範卡片，無法查看細節哦！', type='warning')
        return

    with ui.dialog() as detail_dialog, ui.card().classes('w-[500px] p-6 rounded-2xl'):
        ui.label('🔍 任務詳細情報').classes('text-xl font-extrabold text-blue-900 mb-2')
        ui.label(t['title']).classes('text-lg font-bold text-gray-800 mb-4')
        
        # 顯示基本資訊
        with ui.row().classes('w-full gap-4 text-sm text-gray-600 mb-4 bg-gray-50 p-3 rounded-lg'):
            ui.label(f'👤 主責: {t["owner"] if t["owner"] else "未指定"}')
            ui.label(f'📅 期限: {t["due_date"] if t["due_date"] else "未指定"}')
            ui.label(f'🏷️ 標籤: {t["tag"]}')
        
        # 編輯區
        new_status = ui.select(['規劃中', '待追蹤', '追蹤狀況', '執行中', '卡關'], label='細部狀態', value=t['detailed_status']).classes('w-full mb-2')
        new_notes = ui.textarea('🏢 廠商資訊與追蹤日誌', value=t['vendor_and_notes']).classes('w-full mb-4')
        
        # --- 邏輯定義區 ---
        
        # 1. 儲存修改
        def save_details():
            database.update_task_details(t['id'], new_status.value, new_notes.value)
            ui.notify('💾 情報更新成功！', type='positive', position='top-right')
            detail_dialog.close()
            render_kanban_board.refresh()
            
        # 2. 徹底刪除
        def delete_this_task():
            database.delete_task(t['id'])
            ui.notify('🗑️ 任務已徹底刪除', type='warning', position='top-right')
            detail_dialog.close()
            render_kanban_board.refresh()

        # 3. 🌟 新增：快速完工邏輯
        def quick_complete():
            database.update_task_status(t['id'], '✅ 已完成')
            ui.notify(f'🎉 任務【{t["title"]}】已結案！', type='positive', position='top-right')
            detail_dialog.close()
            render_kanban_board.refresh()

        # --- 底部按鈕區 ---
        with ui.row().classes('w-full justify-between items-center mt-2'):
            # 左側：功能操作區
            with ui.row().classes('gap-1'):
                ui.button('🗑️ 刪除', on_click=delete_this_task, color='red').props('flat text-red-500 hover:bg-red-50')
                
                # 只有在還沒完成的情況下，才顯示完工按鈕
                if t['status'] != '✅ 已完成':
                    ui.button('✅ 標記完工', on_click=quick_complete, color='green').props('flat text-green-600 hover:bg-green-50')
            
            # 右側：存檔/關閉區
            with ui.row().classes('gap-2'):
                ui.button('關閉', on_click=detail_dialog.close, color='gray').props('flat')
                ui.button('💾 儲存修改', on_click=save_details).props('rounded color="primary"')
    
    # 建立完立刻打開
    detail_dialog.open()

# ==========================================
# 🛠️ 模組化工具：生產「動態高階任務卡片」的機器
# ==========================================
def create_rich_card(t):
    urgent_flag = (t['is_urgent'] == 1)
    is_dummy = (t['id'] < 0) # 判斷是不是我們寫死的假卡片
    
    with ui.card().classes('w-full mb-3 cursor-pointer hover:shadow-lg transition-all border-l-4 ' + ('border-red-500' if urgent_flag else 'border-blue-500')):
        with ui.row().classes('w-full justify-between items-start no-wrap'):
            
            # 1. 打勾完成功能 (維持不變)
            def on_checkbox_change(e):
                if e.value and not is_dummy:
                    database.update_task_status(t['id'], '✅ 已完成')
                    ui.notify(f'🎉 恭喜完成：「{t["title"]}」！', type='positive', position='top-right')
                    render_kanban_board.refresh()
            
            is_done = (t['status'] == '✅ 已完成')
            ui.checkbox(t['title'], value=is_done, on_change=on_checkbox_change).classes('font-bold text-gray-800 text-md')

            # 🌟 2. 新增：卡片右側的「情報解鎖」按鈕
            ui.button(icon='info', color='blue-500', on_click=lambda: open_task_detail_modal(t)).props('flat dense rounded').tooltip('查看與編輯情報')
            
        # 團隊黃金需求：負責人與日期 (維持不變)
        if t['owner'] or t['due_date']:
            with ui.row().classes('w-full items-center gap-4 mt-1 pl-8 text-sm text-gray-600'):
                if t['owner']: ui.label(f'👤 {t["owner"]}')
                if t['due_date']: ui.label(f'📅 {t["due_date"]}')

        # 底部標籤區 (維持不變)
        with ui.row().classes('w-full justify-between items-center mt-2 pl-8'):
            ui.label(t['tag']).classes('text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md')
            if urgent_flag:
                ui.label('🔥 今日急件').classes('text-xs text-red-600 font-bold bg-red-100 px-2 py-1 rounded-md')

# ==========================================
# 🛠️ 模組化工具：月曆專用「彩色行程標籤」
# ==========================================
# ==========================================
# 🛠️ 模組化工具：月曆專用「彩色行程標籤」
# ==========================================
def create_event_badge(t):
    color = 'bg-blue-500' if 'A' in t['project_name'] else ('bg-purple-500' if 'B' in t['project_name'] else 'bg-orange-500')
    if t['status'] == '✅ 已完成': color = 'bg-gray-400 line-through'

    badge = ui.label(t['title']).classes(f'text-xs text-white px-2 py-1 rounded truncate cursor-pointer {color} hover:opacity-80 transition-opacity w-full shadow-sm')

    # 🌟 刪掉原本一大串對話框程式碼，改成這簡單的一行呼叫！
    badge.on('click', lambda: open_task_detail_modal(t))

# ==========================================
# 🆕 升級版「新增任務」彈出視窗 (Dialog)
# ==========================================
with ui.dialog() as new_task_dialog, ui.card().classes('w-[500px] p-6 rounded-2xl shadow-2xl'):
    ui.label('✨ 新增戰略任務').classes('text-xl font-extrabold text-blue-900 mb-4')
    
    task_name = ui.input('任務名稱 / 查核點').classes('w-full mb-2')
    with ui.row().classes('w-full gap-2 no-wrap'):
        project_select = ui.select(PROJECT_LIST, label='所屬專案').classes('w-1/2')
        tag_select = ui.select(['行政作業', '數據處理', '現場會勘', '廠商協調', '活動辦理', '其他'], label='任務標籤').classes('w-1/2')

    with ui.row().classes('w-full gap-2 no-wrap mt-2'):
        owner_input = ui.input('👤 主責人員').classes('w-1/2')
        due_date_input = ui.input('📅 預計完成日').props('type="date"').classes('w-1/2')

    with ui.row().classes('w-full gap-2 no-wrap mt-2 items-center'):
        detailed_status_select = ui.select(['規劃中', '待追蹤', '追蹤狀況', '執行中', '卡關'], label='🔍 細部追蹤狀態').classes('w-2/3')
        is_urgent = ui.checkbox('🔥 今日急件').classes('text-red-600 font-bold w-1/3 mt-2')

    vendor_notes_input = ui.textarea('🏢 廠商資訊與追蹤日誌').classes('w-full mt-2')
    ui.separator().classes('my-4')
    
    def save_to_db():
        database.add_task(
            project_name=project_select.value,
            title=task_name.value,
            tag=tag_select.value,
            owner=owner_input.value,
            due_date=due_date_input.value,
            status='📋 待辦事項',
            detailed_status=detailed_status_select.value,
            vendor_and_notes=vendor_notes_input.value,
            is_urgent=1 if is_urgent.value else 0
        )
        ui.notify(f'✅ 已成功將「{task_name.value}」寫入資料庫！', type='positive', position='top-right')
        new_task_dialog.close()
        render_kanban_board.refresh() # 瞬間刷新看板！

    with ui.row().classes('w-full justify-end gap-2'):
        ui.button('取消', on_click=new_task_dialog.close, color='gray').props('flat')
        ui.button('💾 寫入大腦', on_click=save_to_db).props('rounded color="primary"')

# ==========================================
# 🎨 頂部導覽列
# ==========================================
with ui.header(elevated=True).style('background-color: #0f172a').classes('items-center justify-between px-6'):
    with ui.row().classes('items-center'):
        ui.icon('query_stats', size='md').classes('text-white')
        ui.label('專案戰略指揮中心').classes('text-2xl font-bold text-white ml-2')
    ui.button('➕ 新增任務', on_click=new_task_dialog.open, color='blue-500').classes('font-bold shadow-md')

# ==========================================
# 🏠 主體排版與全局大盤：全動態戰略結界
# ==========================================
@ui.refreshable
def render_kanban_board():
    # 1. 向大腦索取所有真實任務
    all_tasks = database.get_all_tasks()

    # ==========================================
    # 📊 區塊 4：全局大進度條 (🌟 已經搬進結界，且擁有真實算力)
    # ==========================================
    with ui.row().classes('w-full max-w-7xl mx-auto mt-6 px-4 gap-6'):
        with ui.card().classes('w-full bg-white shadow-md rounded-xl p-6'):
            ui.label('🏆 專案全局查核點進度').classes('text-lg font-extrabold text-gray-800 mb-4')
            with ui.row().classes('w-full items-center gap-6'):
                
                # 💡 魔法計算機：自動幫清單上的每一個專案畫一個專屬進度條！
                for proj_name in PROJECT_LIST:
                    # 抓出這個專案的所有任務，以及已完成的任務
                    proj_tasks = [t for t in all_tasks if t['project_name'] == proj_name]
                    total_count = len(proj_tasks)
                    done_count = len([t for t in proj_tasks if t['status'] == '✅ 已完成'])
                    
                    # 計算百分比 (防呆機制：如果這個專案還沒建任務，進度就是 0)
                    progress = (done_count / total_count) if total_count > 0 else 0
                    percent_str = f"{int(progress * 100)}%"
                    
                    # 畫出該專案的進度條 (flex-1 讓所有專案自動平分寬度)
                    with ui.column().classes('flex-1 min-w-[200px]'):
                        with ui.row().classes('w-full justify-between items-end mb-1'):
                            ui.label(proj_name).classes('font-bold text-slate-800 truncate')
                            ui.label(f'{percent_str} ({done_count}/{total_count})').classes('text-sm text-gray-500')
                        ui.linear_progress(value=progress, show_value=False).props('color="blue" size="12px rounded"')

        # -----------------------------------
        # ⬅️ 左側面板 (佔比約 30%) - 真實連動版！
        # -----------------------------------
        with ui.column().classes('w-[30%] min-w-[320px] gap-6'):
            
            # 區塊 3：今日必須擊破 (真實急件)
            with ui.card().classes('w-full bg-red-50 border border-red-100 shadow-md'):
                ui.label('🚨 今日必須擊破 (Focus)').classes('text-lg font-extrabold text-red-800 mb-2')
                
                # 💡 魔法 1：自動篩選出「未完成」且「是急件」的任務
                urgent_tasks = [t for t in all_tasks if t['status'] != '✅ 已完成' and t['is_urgent'] == 1]
                
                if not urgent_tasks:
                    ui.label('🎉 太棒了！今天沒有待處理的急件！').classes('text-gray-500 font-bold mt-2')
                else:
                    for t in urgent_tasks:
                        # 直接用我們的卡片製造機畫出來！這代表在左邊也能直接打勾！
                        create_rich_card(t)

            # 區塊 2：動態月曆區
            with ui.card().classes('w-full shadow-md'):
                ui.label('📅 本月查核點 (Milestones)').classes('text-lg font-extrabold text-gray-800 mb-2')
                
                # 💡 魔法 2：讓月曆永遠自動對準真正的「今天」
                from datetime import date
                today_str = date.today().strftime('%Y-%m-%d')
                ui.date(value=today_str).classes('w-full shadow-none')
                
                ui.separator().classes('my-2')
                
                # 💡 魔法 3：抓出有「預計完成日」且未完成的任務，當作查核點提示
                upcoming_tasks = [t for t in all_tasks if t['status'] != '✅ 已完成' and t['due_date']]
                upcoming_tasks.sort(key=lambda x: x['due_date']) # 照日期排隊
                
                if not upcoming_tasks:
                    ui.label('目前沒有即將到來的查核點').classes('text-sm text-gray-500 italic')
                else:
                    # 只顯示最近的 3 筆查核點
                    for t in upcoming_tasks[:3]:
                        with ui.row().classes('w-full items-center gap-2 mb-1 no-wrap'):
                            ui.icon('flag', color='blue' if 'A' in t['project_name'] else 'purple')
                            # 只顯示日期的後段 (例如 03-25) 和標題
                            ui.label(f"{t['due_date'][5:]} - {t['title']}").classes('text-sm font-bold text-gray-700 truncate')

        # -----------------------------------
        # ➡️ 右側面板 (佔比約 70%) - 看板 + 月曆 + 歷史庫
        # -----------------------------------
        with ui.column().classes('flex-1 w-full min-w-[500px]'):
            with ui.card().classes('w-full shadow-md p-0'):
                tab_objects = {}
                
                # 1. 頂部標籤列
                with ui.tabs().classes('w-full bg-slate-100 text-gray-700 font-bold') as tabs:
                    # 🌟 新增：最前面的大月曆標籤
                    tab_calendar = ui.tab('📅 專案總覽大月曆')
                    
                    for proj_name in PROJECT_LIST:
                        tab_objects[proj_name] = ui.tab(proj_name) 
                    tab_archive = ui.tab('🗄️ 歷史成就庫')

                # 2. 標籤對應的面板內容 (預設打開大月曆！)
                with ui.tab_panels(tabs, value=tab_calendar).classes('w-full bg-transparent p-4'):
                    
                    # ==========================================
                    # 🌟 史詩級新戰場：Google 月曆視角
                    # ==========================================
                    with ui.tab_panel(tab_calendar):
                        now = datetime.now()
                        ui.label(f'🗓️ {now.year} 年 {now.month} 月戰情日曆').classes('text-2xl font-extrabold text-gray-800 mb-4')
                        
                        # 畫出 7 欄的網格 (利用背景色跟 gap-px 做出完美的 1px 邊框效果)
                        with ui.grid(columns=7).classes('w-full gap-px bg-gray-300 border border-gray-300 rounded-lg overflow-hidden shadow-sm'):
                            
                            # 畫出星期一到星期日的表頭
                            days_of_week = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
                            for d in days_of_week:
                                with ui.column().classes('bg-slate-100 p-2 items-center justify-center w-full'):
                                    ui.label(d).classes('font-bold text-gray-600 text-sm')
                            
                            # 計算這個月的日曆排列 (firstweekday=6 代表從週日開始)
                            cal = calendar.Calendar(firstweekday=6)
                            month_days = cal.monthdayscalendar(now.year, now.month)
                            
                            # 畫出每一天的格子
                            for week in month_days:
                                for day in week:
                                    # 每一格的底色與設定
                                    with ui.column().classes('bg-white p-2 min-h-[120px] w-full justify-start items-stretch gap-1'):
                                        if day == 0:
                                            # 這格不屬於這個月
                                            ui.label('').classes('text-gray-300')
                                        else:
                                            # 印出日期數字
                                            is_today = (day == now.day)
                                            day_label = ui.label(str(day)).classes('text-sm font-bold mb-1 ' + ('text-white bg-blue-600 rounded-full w-6 h-6 flex items-center justify-center' if is_today else 'text-gray-500'))
                                            
                                            # 🔍 從大腦撈出「期限是這一天」的任務，塞進格子裡！
                                            current_date_str = f"{now.year}-{now.month:02d}-{day:02d}"
                                            day_tasks = [t for t in all_tasks if t['due_date'] == current_date_str]
                                            
                                            for t in day_tasks:
                                                create_event_badge(t)

                    # ==========================================
                    # 專案 A、B、C 看板 (維持不變)
                    # ==========================================
                    for proj_name in PROJECT_LIST:
                        with ui.tab_panel(tab_objects[proj_name]):
                            with ui.row().classes('w-full items-start gap-4 no-wrap overflow-x-auto'):
                                my_proj_tasks = [t for t in all_tasks if t['project_name'] == proj_name]
                                
                                with ui.column().classes('w-1/2 bg-slate-50 p-4 rounded-xl'):
                                    ui.label('📋 執行中事項').classes('font-bold text-gray-700 mb-2')
                                    for t in my_proj_tasks:
                                        if t['status'] == '📋 待辦事項':
                                            create_rich_card(t)
                                
                                with ui.column().classes('w-1/2 bg-orange-50 p-4 rounded-xl'):
                                    ui.label('🛑 等待外部回覆 (Blocked)').classes('font-bold text-orange-800 mb-2')
                                    for t in my_proj_tasks:
                                        if t['status'] == '🛑 卡關中':
                                            create_rich_card(t)

                    # ==========================================
                    # 🌟 神級進化：可互動的歷史成就庫
                    # ==========================================
                    with ui.tab_panel(tab_archive):
                        with ui.row().classes('w-full justify-between items-center mb-4'):
                            ui.label('🏆 專案歷史結算紀錄').classes('text-lg font-bold text-gray-800')
                            ui.button('📥 匯出 Excel', color='green').props('rounded outline icon="download"')
                        
                        # 1. 欄位定義：多加一個名為 'actions' (操作) 的欄位
                        columns = [
                            {'name': 'date', 'label': '完成日期', 'field': 'date', 'sortable': True, 'align': 'left'},
                            {'name': 'project', 'label': '所屬專案', 'field': 'project', 'sortable': True, 'align': 'left'},
                            {'name': 'task', 'label': '任務名稱 / 查核點', 'field': 'task', 'align': 'left'},
                            {'name': 'tag', 'label': '標籤', 'field': 'tag', 'align': 'center'},
                            {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'} # 🌟 新增的操作欄位
                        ]
                        
                        # 2. 資料準備：把任務的 id 也偷偷塞進表格資料裡，這樣按鈕才知道要操作誰
                        completed_tasks = [t for t in all_tasks if t['status'] == '✅ 已完成']
                        rows = [
                            {
                                'id': t['id'], # 🌟 隱藏的身分證
                                'date': t['due_date'] if t['due_date'] else '-', 
                                'project': t['project_name'], 
                                'task': t['title'], 
                                'tag': t['tag']
                            } for t in completed_tasks
                        ]
                        
                        # 3. 召喚表格元件
                        history_table = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')

                        # ==========================================
                        # 🧠 定義三個按鈕被按下時的大腦反應
                        # ==========================================
                        # 【復原任務】
                        def handle_restore(e):
                            task_id = e.args['id']
                            database.update_task_status(task_id, '📋 待辦事項') # 改回待辦狀態
                            ui.notify('↩️ 任務已復原，請回看板查看！', type='info', position='top-right')
                            render_kanban_board.refresh() # 瞬間刷新

                        # 【刪除任務】
                        def handle_delete(e):
                            task_id = e.args['id']
                            database.delete_task(task_id) # 徹底抹除
                            ui.notify('🗑️ 歷史紀錄已徹底刪除！', type='warning', position='top-right')
                            render_kanban_board.refresh() # 瞬間刷新
                            
                        # 【檢視任務】
                        def handle_view(e):
                            task_id = e.args['id']
                            # 從大腦記憶中把這包任務的完整情報找出來
                            t = next((task for task in all_tasks if task['id'] == task_id), None)
                            if t:
                                # 彈出唯讀的歷史情報視窗
                                with ui.dialog() as view_dialog, ui.card().classes('w-[500px] p-6 rounded-2xl'):
                                    ui.label('🔍 歷史任務歸檔情報').classes('text-xl font-extrabold text-gray-700 mb-2')
                                    ui.label(t['title']).classes('text-lg font-bold text-gray-800 mb-4')
                                    ui.label(f'負責人: {t["owner"] if t["owner"] else "未指定"} | 期限: {t["due_date"]}').classes('text-sm text-gray-600 mb-4')
                                    ui.textarea('🏢 廠商資訊與追蹤日誌 (已歸檔)', value=t['vendor_and_notes']).classes('w-full mb-4').props('readonly')
                                    ui.button('關閉', on_click=view_dialog.close).props('rounded color="gray" w-full')
                                view_dialog.open()

                        # 4. 把大腦反應綁定到表格上
                        history_table.on('restore', handle_restore)
                        history_table.on('delete', handle_delete)
                        history_table.on('view', handle_view)

                        # 🌟 5. 黑科技魔法插槽：利用前端框架語法，在最後一欄畫出三個漂亮的圖示按鈕
                        history_table.add_slot('body-cell-actions', '''
                            <q-td :props="props">
                                <q-btn flat dense round color="blue" icon="visibility" @click="() => $parent.$emit('view', props.row)" />
                                <q-btn flat dense round color="green" icon="undo" @click="() => $parent.$emit('restore', props.row)" />
                                <q-btn flat dense round color="red" icon="delete" @click="() => $parent.$emit('delete', props.row)" />
                            </q-td>
                        ''')

# 呼叫並畫出這個結界
render_kanban_board()

# ==========================================
# 🚀 啟動伺服器
# ==========================================
ui.run(title='戰略指揮中心', favicon='🔥')