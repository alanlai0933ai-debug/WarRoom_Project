from nicegui import app, ui 
import database
import calendar        
from datetime import datetime 
import ui_components 
import os
import csv
import io  # 🌟 處理 CSV 匯入必須的套件

# 🌟 第一步：確認資料庫存在與升級
database.init_db()
database.upgrade_db_schema()

# ==========================================
# 🧠 系統設定 (全域變數)
# ==========================================
PROJECT_LIST = [
    '🌊 專案 A (海岸清理)',
    '🏛️ 專案 B (新北巡檢)',
    '🌱 專案 C (臨時交辦事項)'
]

# ==========================================
# 終極視覺革命：Sleek Pro Dark (極簡專業暗黑主題)
# ==========================================
pro_dark_theme = '''
body { background-color: #0f172a !important; color: #f8fafc !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; }
.q-card { background: #1e293b !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 12px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important; color: #f1f5f9 !important; }
.bg-red-900\\/20 { background: rgba(127, 29, 29, 0.15) !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; border-left: 4px solid #ef4444 !important; }
.q-tab { color: #94a3b8 !important; }
.q-tab--active { color: #38bdf8 !important; }
.q-btn--outline { border-color: rgba(255, 255, 255, 0.15) !important; color: #e2e8f0 !important; }
.q-field--outlined .q-field__control { background: #0f172a !important; border-radius: 8px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }
.q-field__native, .q-field__prefix, .q-field__suffix, .q-field__input { color: #f8fafc !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; border: 2px solid #0f172a; }
::-webkit-scrollbar-thumb:hover { background: #475569; }
'''

# ==========================================
# 🛡️ 終極防護罩：Firebase Google 登入引擎
# ==========================================
firebase_js = '''
<script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js"></script>
<script>
  const firebaseConfig = {
    apiKey: "AIzaSyAq1hfpgcTDaVm2RSd6m-ny8mSiy9tDE94",
    authDomain: "warroom-f3e51.firebaseapp.com",
    projectId: "warroom-f3e51",
    storageBucket: "warroom-f3e51.firebasestorage.app",
    messagingSenderId: "531055949529",
    appId: "1:531055949529:web:8055c85c0a78c1efbc30c8"
  };
  if (!firebase.apps.length) { firebase.initializeApp(firebaseConfig); }
  const auth = firebase.auth();
  const provider = new firebase.auth.GoogleAuthProvider();
  async function signInWithGoogle() {
      try {
          const result = await auth.signInWithPopup(provider);
          const user = result.user;
          return { name: user.displayName, email: user.email, photo: user.photoURL };
      } catch (error) { console.error(error); return { error: error.message }; }
  }
  async function signOutGoogle() { await auth.signOut(); }
</script>
'''

@ui.page('/')
async def main_page():
    ui.add_head_html(f'<style>{pro_dark_theme}</style>\n{firebase_js}')

    # 🔒 安全檢查點 (已完美置中縮排)
    if not app.storage.user.get('authenticated', False):
        with ui.column().classes('w-full h-screen items-center justify-center bg-slate-900'):
            ui.icon('admin_panel_settings', size='100px', color='blue-500').classes('mb-4')
            ui.label('專案戰略指揮中心').classes('text-4xl font-extrabold text-white mb-2 tracking-widest')
            ui.label('Project War Room - Secure Access').classes('text-slate-400 mb-8 tracking-widest')
            
            with ui.card().classes('p-8 bg-slate-800 items-center rounded-2xl shadow-2xl border border-slate-700 w-96'):
                ui.label('系統權限驗證').classes('text-xl font-bold text-slate-200 mb-6')
                
                async def perform_login():
                    result = await ui.run_javascript('signInWithGoogle()', timeout=120.0)
                    if result and 'email' in result:
                        ALLOWED_EMAILS = ['alanlai0933.ai@gmail.com', 'alanlai0933@gmail.com', 'coastalcleanup00@gmail.com']
                        if result['email'] in ALLOWED_EMAILS:
                            app.storage.user.update({'authenticated': True, 'email': result['email'], 'name': result['name'], 'avatar': result['photo']})
                            ui.notify(f"歡迎指揮官：{result['name']} 歸隊！", type='positive', position='top')
                            ui.navigate.to('/')
                        else:
                            ui.notify(f'警告：信箱 {result["email"]} 未獲授權！', type='negative', position='top')
                    else:
                        error_msg = result.get('error', '未知錯誤') if result else '取消登入'
                        ui.notify(f'登入失敗：{error_msg}', type='negative', position='top')
                
                ui.button('使用 Google 帳號登入', icon='login', on_click=perform_login).props('rounded color="blue-600" size="lg"').classes('w-full font-bold shadow-lg')
        return
# ✅ 進入戰略看板區
    app_state = {
        'selected_year': 115,  # 預設 115 年度
        'current_tab': '📅 專案總覽大月曆',
        'expanded_tasks': set(),  
        'search_query': '',
        'calendar_year': datetime.now().year,    
        'calendar_month': datetime.now().month   
    }

    # 🌟 批次匯入引擎 (支援母帶子與年度標記)
    async def handle_csv_upload(e):
        content = e.content.read().decode('utf-8-sig')
        f = io.StringIO(content)
        reader = csv.DictReader(f)
        all_tasks_now = database.get_all_tasks()
        name_to_id = {t['title']: t['id'] for t in all_tasks_now}
        count = 0
        try:
            for row in reader:
                parent_name = row.get('母任務名稱', '').strip()
                parent_id = name_to_id.get(parent_name) if parent_name else None
                database.add_task(
                    project_name=row['專案名稱'], title=row['任務名稱'], tag=row.get('標籤', '未分類'),
                    owner=row.get('主責人員', '未分配'), due_date=row.get('預計完成時間', ''),
                    status=row.get('狀態', '📋 待辦事項'), detailed_status='', vendor_and_notes='',
                    is_urgent=int(row.get('是否急件', 0)), parent_id=parent_id,
                    weight=int(row.get('權重', 1)), target_total=int(row.get('目標總數', 1)),
                    year=app_state['selected_year'] # 自動打上當前選擇的年度
                )
                if not parent_id: 
                    new_all = database.get_all_tasks()
                    if new_all: name_to_id[new_all[-1]['title']] = new_all[-1]['id']
                count += 1
            ui.notify(f'🚀 成功匯入 {count} 筆資料！', type='positive', position='top')
            render_kanban_board.refresh()
            upload_dialog.close()
        except Exception as err:
            ui.notify(f'❌ 匯入失敗：{str(err)}', type='negative', position='top')

    # ==========================================
    # 🎨 頂部導覽列 (年度切換、匯入按鈕、登出)
    # ==========================================
    with ui.header(elevated=True).style('background-color: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px);').classes('items-center justify-between px-6 border-b border-white/10'):
        with ui.row().classes('items-center'):
            ui.icon('query_stats', size='md').classes('text-blue-400')
            ui.label('專案戰略指揮中心').classes('text-2xl font-bold text-white ml-2 tracking-wider')
            
            with ui.row().classes('items-center ml-8 px-4 py-1 bg-white/5 rounded-lg border border-white/10'):
                ui.label('執行年度:').classes('text-slate-400 text-sm mr-2')
                ui.select(
                    options=[113, 114, 115, 116], value=app_state['selected_year'], 
                    on_change=lambda e: (app_state.update(selected_year=e.value), render_kanban_board.refresh(), ui.notify(f'切換至 {e.value} 年度', type='info'))
                ).props('dark dense borderless').classes('w-20 text-blue-400 font-bold')

        with ui.row().classes('items-center gap-4'):
            ui.button('📥 批次匯入', on_click=lambda: upload_dialog.open(), color='slate-700').props('outline rounded size="sm"')
            
            if app.storage.user.get('avatar'):
                ui.image(app.storage.user.get('avatar')).classes('w-8 h-8 rounded-full border border-slate-500')
            ui.label(app.storage.user.get('name', '未知名稱')).classes('text-slate-200 font-bold')
            
            async def perform_logout():
                await ui.run_javascript('signOutGoogle()')
                app.storage.user.clear()
                ui.notify('已安全登出系統', type='info', position='top')
                ui.navigate.to('/')
                
            ui.button('登出', on_click=perform_logout, color='slate-700').props('outline rounded size="sm" text-color="white"')
            ui.button('➕ 新增任務', on_click=lambda: ui_components.open_new_task_dialog(PROJECT_LIST, render_kanban_board.refresh, app_state['selected_year']), color='blue-600').classes('font-bold shadow-lg')


    # 🔍 全局搜尋區
    def update_search(e):
        app_state['search_query'] = e.value
        render_kanban_board.refresh() 

    with ui.row().classes('w-full max-w-7xl mx-auto mt-6 px-4'):
        ui.input('🔍 全局智慧搜尋 (支援：任務名稱 / 負責人 / 標籤 / 日誌 / 狀態)', value=app_state['search_query'], on_change=update_search).classes('w-full text-lg').props('clearable outlined dark rounded-xl shadow-sm debounce="500"')
# ==========================================
    # 🏠 主體排版與看板邏輯
    # ==========================================
    @ui.refreshable
    def render_kanban_board():
        # 🌟 核心過濾：只撈取符合當前選擇年度的任務
        all_tasks = [t for t in database.get_all_tasks() if t.get('year') == app_state['selected_year']]

        needs_refresh = False
        for p in [t for t in all_tasks if not t.get('parent_id') and t.get('status') != '✅ 已完成']:
            children = [c for c in all_tasks if c.get('parent_id') == p['id']]
            if children and all(c.get('status') == '✅ 已完成' for c in children):
                database.update_task_status(p['id'], '✅ 已完成')
                ui.notify(f'🎊 捷報！子任務達成，大項目自動通關！', type='positive', position='top')
                needs_refresh = True 
        if needs_refresh: 
            all_tasks = [t for t in database.get_all_tasks() if t.get('year') == app_state['selected_year']]

        def get_task_earned(t):
            if t.get('status') == '✅ 已完成': return t.get('weight', 1)
            target = t.get('target_total', 1)
            prog = t.get('current_progress', 0)
            if target > 1: return (prog / target) * t.get('weight', 1)
            return 0

        query = app_state['search_query'].lower()
        if query:
            matched_ids = set()
            for t in all_tasks:
                search_text = f"{t.get('title','')} {t.get('tag','')} {t.get('owner','')} {t.get('detailed_status','')} {t.get('vendor_and_notes','')} {t.get('project_name','')}".lower()
                if query in search_text: matched_ids.add(t['id'])

            final_ids = set(matched_ids)
            for t in all_tasks:
                if t['id'] in matched_ids and t.get('parent_id'): final_ids.add(t['parent_id']) 
                if t.get('parent_id') in matched_ids: final_ids.add(t['id'])        
            display_tasks = [t for t in all_tasks if t['id'] in final_ids]
        else: display_tasks = all_tasks

        with ui.row().classes('w-full max-w-7xl mx-auto mt-4 px-4 gap-6'):
            
            with ui.card().classes('w-full shadow-lg rounded-xl p-6 border-t-4 border-blue-500 bg-white/5 backdrop-blur-md'):
                ui.label('🏆 專案加權實獲值 (EVM) 總盤').classes('text-lg font-extrabold text-gray-100 mb-4 tracking-wide')
                with ui.row().classes('w-full items-center gap-6'):
                    for proj_name in PROJECT_LIST:
                        proj_tasks = [t for t in all_tasks if t['project_name'] == proj_name]
                        top_tasks = [t for t in proj_tasks if not t.get('parent_id')]
                        
                        total_proj_weight = sum(t.get('weight', 1) for t in top_tasks)
                        earned_proj_weight = 0
                        for p_task in top_tasks:
                            children = [c for c in proj_tasks if c.get('parent_id') == p_task['id']]
                            if children:
                                c_total = sum(c.get('weight', 1) for c in children)
                                c_earned = sum(get_task_earned(c) for c in children)
                                earned_proj_weight += (c_earned / c_total) * p_task.get('weight', 1) if c_total > 0 else 0
                            else:
                                earned_proj_weight += get_task_earned(p_task)
                        
                        progress = (earned_proj_weight / total_proj_weight) if total_proj_weight > 0 else 0
                        percent_str = f"{int(progress * 100)}%"
                        
                        with ui.column().classes('flex-1 min-w-[200px]'):
                            with ui.row().classes('w-full justify-between items-end mb-1'):
                                ui.label(proj_name).classes('font-bold text-slate-200 truncate')
                                ui.label(f'{percent_str} (權分 {earned_proj_weight:.1f} / {total_proj_weight:.1f})').classes('text-sm text-blue-400 font-bold')
                            ui.linear_progress(value=progress, show_value=False).props('color="blue-4" size="12px rounded"')

            with ui.column().classes('w-[30%] min-w-[320px] gap-6'):
                with ui.card().classes('w-full bg-red-900/20 border border-red-500/30 shadow-md backdrop-blur-md'):
                    ui.label('🚨 今日必須擊破 (Focus)').classes('text-lg font-extrabold text-red-400 mb-2 tracking-wide')
                    urgent_tasks = [t for t in display_tasks if t['status'] != '✅ 已完成' and t['is_urgent'] == 1]
                    if not urgent_tasks: ui.label('🎉 今日目前無急件！').classes('text-gray-400 font-bold mt-2')
                    else:
                        with ui.column().classes('w-full max-h-[350px] overflow-y-auto pr-2 pb-2'):
                            for t in urgent_tasks: ui_components.create_rich_card(t, display_tasks, app_state, render_kanban_board.refresh)

                with ui.card().classes('w-full bg-white/5 border border-white/10 shadow-md backdrop-blur-md'):
                    ui.label('📅 近期查核點 (Upcoming)').classes('text-lg font-extrabold text-gray-200 mb-2 tracking-wide')
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    upcoming_tasks = [t for t in display_tasks if t['status'] != '✅ 已完成' and t['due_date'] and t['due_date'] >= today_str]
                    upcoming_tasks.sort(key=lambda x: x['due_date']) 
                    if not upcoming_tasks: ui.label('目前沒有即將到來的查核點').classes('text-sm text-gray-400 italic')
                    else:
                        with ui.column().classes('w-full max-h-[350px] overflow-y-auto pr-2 pb-2'):
                            for t in upcoming_tasks: ui_components.create_rich_card(t, display_tasks, app_state, render_kanban_board.refresh, is_subtask=True)
            with ui.column().classes('flex-1 w-full min-w-[500px]'):
                with ui.card().classes('w-full shadow-md p-0 bg-transparent border border-white/10 overflow-hidden'):
                    tab_objects = {}
                    with ui.tabs().classes('w-full bg-white/5 text-gray-300 font-bold') as tabs:
                        tab_calendar = ui.tab('📅 專案總覽大月曆')
                        for proj_name in PROJECT_LIST: tab_objects[proj_name] = ui.tab(proj_name) 
                        tab_archive = ui.tab('🗄️ 歷史成就庫')

                    with ui.tab_panels(tabs, value=app_state['current_tab'], on_change=lambda e: app_state.update(current_tab=e.value)).classes('w-full bg-transparent p-4'):                    
                        with ui.tab_panel(tab_calendar):
                            c_year = app_state['calendar_year']
                            c_month = app_state['calendar_month']
                            now = datetime.now()

                            def prev_month():
                                if app_state['calendar_month'] == 1: app_state['calendar_month'] = 12; app_state['calendar_year'] -= 1
                                else: app_state['calendar_month'] -= 1
                                render_kanban_board.refresh()
                                
                            def next_month():
                                if app_state['calendar_month'] == 12: app_state['calendar_month'] = 1; app_state['calendar_year'] += 1
                                else: app_state['calendar_month'] += 1
                                render_kanban_board.refresh()
                                
                            def go_today():
                                app_state['calendar_year'] = now.year; app_state['calendar_month'] = now.month
                                render_kanban_board.refresh()

                            with ui.row().classes('w-full justify-between items-center mb-4'):
                                ui.label(f'🗓️ {c_year} 年 {c_month} 月戰情日曆').classes('text-2xl font-extrabold text-gray-100')
                                with ui.row().classes('gap-2'):
                                    ui.button('◀ 上個月', on_click=prev_month, color='slate-700').props('outline rounded size="sm" text-color="white"')
                                    ui.button('⏺ 回到本月', on_click=go_today, color='blue-500').props('outline rounded size="sm" text-color="blue-3"')
                                    ui.button('下個月 ▶', on_click=next_month, color='slate-700').props('outline rounded size="sm" text-color="white"')

                            with ui.grid(columns=7).classes('w-full gap-px bg-slate-700 border border-slate-700 rounded-lg overflow-hidden shadow-sm'):
                                for d in ['週日', '週一', '週二', '週三', '週四', '週五', '週六']:
                                    with ui.column().classes('bg-white/10 p-2 items-center justify-center w-full'): ui.label(d).classes('font-bold text-gray-300 text-sm')
                                month_days = calendar.Calendar(firstweekday=6).monthdayscalendar(c_year, c_month)
                                for week in month_days:
                                    for day in week:
                                        with ui.column().classes('bg-slate-900/60 p-2 min-h-[120px] w-full justify-start items-stretch gap-1 hover:bg-slate-800/80 transition-colors'):
                                            if day == 0: ui.label('').classes('text-gray-300')
                                            else:
                                                is_today = (day == now.day and c_month == now.month and c_year == now.year)
                                                ui.label(str(day)).classes('text-sm font-bold mb-1 ' + ('text-white bg-blue-600 rounded-full w-6 h-6 flex items-center justify-center shadow-lg shadow-blue-500/50' if is_today else 'text-gray-400'))
                                                d_str = f"{c_year}-{c_month:02d}-{day:02d}"
                                                for t in [t for t in display_tasks if t['due_date'] == d_str]: ui_components.create_event_badge(t, render_kanban_board.refresh)

                        for proj_name in PROJECT_LIST:
                            with ui.tab_panel(tab_objects[proj_name]):
                                with ui.row().classes('w-full items-start gap-4 no-wrap overflow-x-auto'):
                                    top_level_tasks = [t for t in display_tasks if t['project_name'] == proj_name and not t.get('parent_id')]
                                    with ui.column().classes('w-1/2 bg-white/5 p-4 rounded-xl border border-white/10'):
                                        ui.label('📋 執行中事項').classes('font-bold text-gray-200 mb-2')
                                        for t in top_level_tasks:
                                            if t.get('status') == '📋 待辦事項': ui_components.create_rich_card(t, display_tasks, app_state, render_kanban_board.refresh)
                                    with ui.column().classes('w-1/2 bg-orange-500/10 p-4 rounded-xl border border-orange-500/20'):
                                        ui.label('🛑 等待外部回覆 (Blocked)').classes('font-bold text-orange-300 mb-2')
                                        for t in top_level_tasks:
                                            if t.get('status') == '🛑 卡關中': ui_components.create_rich_card(t, display_tasks, app_state, render_kanban_board.refresh)

                        with ui.tab_panel(tab_archive):
                            with ui.row().classes('w-full justify-between items-center mb-4'):
                                ui.label('🏆 專案歷史結算紀錄').classes('text-lg font-bold text-gray-100 tracking-wide')
                                def export_to_excel():
                                    filename = f'專案戰情結算報告_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
                                    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                                        writer = csv.writer(f)
                                        writer.writerow(['完成日期', '所屬專案', '任務名稱 / 查核點', '權重', '目標達成數', '標籤', '追蹤日誌'])
                                        for t in [t for t in display_tasks if t['status'] == '✅ 已完成']:
                                            writer.writerow([t['due_date'] if t['due_date'] else '-', t['project_name'], t['title'], t.get('weight', 1), f"{t.get('current_progress', 0)} / {t.get('target_total', 1)}", t['tag'], t.get('vendor_and_notes', '')])
                                    ui.download(filename); ui.notify('📥 報表已成功下載！', type='positive', position='top')
                                ui.button('📥 匯出 EXCEL', on_click=export_to_excel, color='green-6').props('rounded outline icon="download" shadow')
                            
                            columns = [{'name': 'date', 'label': '完成日期', 'field': 'date', 'align': 'left'}, {'name': 'project', 'label': '專案', 'field': 'project', 'align': 'left'}, {'name': 'task', 'label': '任務', 'field': 'task', 'align': 'left'}, {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'}]
                            rows = [{'id': t['id'], 'date': t['due_date'] if t['due_date'] else '-', 'project': t['project_name'], 'task': t['title']} for t in display_tasks if t['status'] == '✅ 已完成']
                            history_table = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full bg-transparent').props('dark flat bordered')
                            def handle_restore(e): database.update_task_status(e.args['id'], '📋 待辦事項'); ui.notify('↩️ 已復原', type='info'); render_kanban_board.refresh() 
                            def handle_delete(e): database.delete_task(e.args['id']); ui.notify('🗑️ 已刪除', type='warning'); render_kanban_board.refresh() 
                            def handle_view(e):
                                t = next((task for task in all_tasks if task['id'] == e.args['id']), None)
                                if t: ui_components.open_task_detail_modal(t, render_kanban_board.refresh) 
                            history_table.on('restore', handle_restore); history_table.on('delete', handle_delete); history_table.on('view', handle_view)
                            history_table.add_slot('body-cell-actions', '''<q-td :props="props"><q-btn flat dense round color="blue-4" icon="visibility" @click="() => $parent.$emit('view', props.row)" /><q-btn flat dense round color="green-4" icon="undo" @click="() => $parent.$emit('restore', props.row)" /><q-btn flat dense round color="red-4" icon="delete" @click="() => $parent.$emit('delete', props.row)" /></q-td>''')

    # 隱藏的匯入對話框組件 (放在 render_kanban_board 之外)
    with ui.dialog() as upload_dialog, ui.card().classes('p-6 bg-slate-800 border border-slate-700'):
        ui.label('批次匯入任務 (CSV)').classes('text-xl font-bold text-white mb-4')
        ui.label('將根據上方選擇的「執行年度」進行標記').classes('text-slate-400 mb-4')
        ui.upload(on_upload=handle_csv_upload, auto_upload=True).classes('w-full').props('dark flat')
        ui.button('關閉', on_click=upload_dialog.close).props('flat').classes('mt-4')

    render_kanban_board()

# ==========================================
# 🛡️ 資安與系統啟動區 (修復本地端啟動報錯)
# ==========================================
SECRET_KEY = os.environ.get('WAR_ROOM_SECRET', 'local_development_fallback_secret_12345')

# 🌟 關鍵保護：允許多執行緒啟動
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host='0.0.0.0', 
        port=8080, 
        title='戰略指揮中心', 
        favicon='🔥', 
        dark=True, 
        storage_secret=SECRET_KEY, 
        uvicorn_reload_includes='*.py,*.css'
    )