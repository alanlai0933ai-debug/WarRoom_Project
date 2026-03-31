from nicegui import ui
import database

# ==========================================
# 🎨 視覺進化：高質感暗黑標籤色彩字典
# ==========================================
TAG_COLORS = {
    '行政作業': 'bg-slate-700 text-slate-300',
    '數據處理': 'bg-blue-900/40 text-blue-300 border border-blue-700/50',
    '現場會勘': 'bg-emerald-900/40 text-emerald-300 border border-emerald-700/50',
    '追蹤日誌': 'bg-purple-900/40 text-purple-300 border border-purple-700/50',
    '活動辦理': 'bg-pink-900/30 text-pink-300 border border-pink-700/50',
    '其他': 'bg-gray-800 text-gray-400 border border-gray-700/50',
    '一般': 'bg-slate-700 text-slate-300'
}

# ==========================================
# 🛠️ 模組化工具 1：唯一情報詳細視窗 (全功能編輯版 + 一鍵分裂)
# ==========================================
def open_task_detail_modal(t, refresh_cb):
    if t.get('id', -1) < 0:
        ui.notify('這是示範卡片，無法查看細節哦！', type='warning')
        return

    all_tasks = database.get_all_tasks()
    
    project_list = list(set([task['project_name'] for task in all_tasks if task.get('project_name')]))
    if not project_list: project_list = ['專案 A', '專案 B', '專案 C']
    if t['project_name'] not in project_list: project_list.append(t['project_name'])

    with ui.dialog() as detail_dialog, ui.card().classes('w-[600px] p-6 rounded-2xl'):
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('🔍 任務詳細情報 (全功能編輯)').classes('text-xl font-extrabold text-blue-400')
            def spawn_subtask():
                detail_dialog.close()
                open_new_task_dialog(project_list, refresh_cb, default_parent_id=t['id'], default_project=t['project_name'])
            ui.button('➕ 新增子任務', on_click=spawn_subtask, color='purple-600').props('rounded size="sm" icon="account_tree" shadow')

        new_title = ui.input('任務名稱 / 查核點', value=t['title']).classes('w-full mb-2 text-lg font-bold').props('dark outlined')
        
        with ui.row().classes('w-full gap-2 no-wrap mb-2'):
            new_project = ui.select(project_list, label='所屬專案', value=t['project_name']).classes('w-1/2').props('dark outlined')
            
            # 🛡️ 標籤防呆
            current_tag = t.get('tag')
            if not current_tag: current_tag = '一般'
            tag_options = ['行政作業', '數據處理', '現場會勘', '追蹤日誌', '活動辦理', '一般', '其他']
            if current_tag not in tag_options: tag_options.append(current_tag)
            new_tag = ui.select(tag_options, label='任務標籤', value=current_tag).classes('w-1/2').props('dark outlined')

        with ui.row().classes('w-full gap-2 no-wrap mb-2'):
            # 🌟 完美平衡：換回下拉選單，並在 Label 加上溫馨提示
            owner_list = list(set([task['owner'] for task in all_tasks if task.get('owner')]))
            if '未指定' not in owner_list: owner_list.insert(0, '未指定')
            current_owner = t.get('owner') if t.get('owner') else '未指定'
            if current_owner not in owner_list: owner_list.append(current_owner)
            
            new_owner = ui.select(owner_list, label='👤 主責人員 (新名字請按 Enter)', value=current_owner, with_input=True, new_value_mode='add-unique').classes('w-1/2').props('dark outlined')
            new_due_date = ui.input('📅 期限', value=t.get('due_date', '')).props('type="date" dark outlined').classes('w-1/2')

        with ui.row().classes('w-full gap-2 no-wrap mb-2 items-center bg-slate-800/60 p-3 rounded-lg border border-slate-700'):
            new_weight = ui.number('⚖️ 權重', value=t.get('weight', 1), min=1).classes('w-1/3').props('dark outlined')
            new_target = ui.number('🎯 目標總數', value=t.get('target_total', 1), min=1).classes('w-1/3').props('dark outlined')
            new_is_urgent = ui.checkbox('🔥 今日急件', value=bool(t.get('is_urgent', 0))).classes('text-red-400 font-bold w-1/3 mt-2').props('dark')

        with ui.row().classes('w-full gap-2 no-wrap mb-2'):
            # 🛡️ 狀態防呆
            current_status = t.get('detailed_status')
            if not current_status: current_status = '規劃中'
            status_options = ['規劃中', '待追蹤', '追蹤狀況', '執行中', '卡關']
            if current_status not in status_options: status_options.append(current_status)
            new_status = ui.select(status_options, label='細部狀態', value=current_status).classes('w-full').props('dark outlined')
        
        new_notes = ui.textarea('🏢 追蹤日誌', value=t.get('vendor_and_notes', '')).classes('w-full mb-4').props('dark outlined')
        
        def save_details():
            database.update_task_full(
                task_id=t['id'], title=new_title.value, project_name=new_project.value,
                tag=new_tag.value, owner=new_owner.value, due_date=new_due_date.value,
                weight=int(new_weight.value), target_total=int(new_target.value),
                is_urgent=1 if new_is_urgent.value else 0, detailed_status=new_status.value,
                vendor_and_notes=new_notes.value
            )
            ui.notify('💾 任務情報全面更新成功！', type='positive', position='top-right')
            detail_dialog.close()
            refresh_cb() 

        def delete_this_task():
            database.delete_task(t['id'])
            ui.notify('🗑️ 任務已徹底刪除', type='warning', position='top-right')
            detail_dialog.close()
            refresh_cb()

        def quick_complete():
            database.update_task_status(t['id'], '✅ 已完成')
            ui.notify(f'🎉 任務【{t["title"]}】已結案！', type='positive', position='top-right')
            detail_dialog.close()
            refresh_cb()

        def mark_blocked():
            database.update_task_status(t['id'], '🛑 卡關中')
            ui.notify('🛑 任務已移至【等待外部回覆】', type='warning', position='top-right')
            detail_dialog.close()
            refresh_cb()
            
        def resume_task():
            database.update_task_status(t['id'], '📋 待辦事項')
            ui.notify('▶️ 任務已恢復執行！', type='info', position='top-right')
            detail_dialog.close()
            refresh_cb()

        with ui.row().classes('w-full justify-between items-center mt-2 pt-4 border-t border-slate-700'):
            with ui.row().classes('gap-1'):
                ui.button('🗑️ 刪除', on_click=delete_this_task, color='red-500').props('flat px-2')
                if t['status'] != '✅ 已完成':
                    if t['status'] == '🛑 卡關中': ui.button('▶️ 恢復執行', on_click=resume_task, color='blue-400').props('flat px-2')
                    else: ui.button('🛑 標記卡關', on_click=mark_blocked, color='orange-400').props('flat px-2')
                    ui.button('✅ 標記完工', on_click=quick_complete, color='green-400').props('flat px-2')
            with ui.row().classes('gap-2'):
                ui.button('關閉', on_click=detail_dialog.close, color='slate-500').props('flat')
                ui.button('💾 儲存所有修改', on_click=save_details).props('rounded color="primary" shadow')
    detail_dialog.open()

# ==========================================
# 🛠️ 模組化工具 2：具備記憶與容錯的巢狀卡片 
# ==========================================
def create_rich_card(t, all_tasks, app_state, refresh_cb, is_subtask=False):
    urgent_flag = (t.get('is_urgent', 0) == 1)
    is_dummy = (t.get('id', -1) < 0)
    
    if is_subtask:
        card_style = 'w-full mb-2 cursor-pointer transition-all border-l-4 border-slate-500 bg-slate-800/40 p-2 hover:bg-slate-700/50 group'
    else:
        card_style = 'w-full mb-3 cursor-pointer transition-all border-l-4 p-3 group hover:bg-slate-700/40 ' + ('border-red-500 bg-red-900/10' if urgent_flag else 'border-blue-500 bg-transparent')

    with ui.card().classes(card_style) as card:
        if not is_dummy:
            card.on('click', lambda e: open_task_detail_modal(t, refresh_cb))

        if not is_dummy:
            with ui.row().classes('w-full items-center gap-1 mb-2 text-xs font-bold no-wrap overflow-hidden'):
                ui.label(t.get('project_name', '未知專案')).classes('bg-slate-700 text-slate-300 px-2 py-0.5 rounded truncate max-w-[140px]')
                parent_id = t.get('parent_id')
                if parent_id:
                    parent_task = next((p for p in all_tasks if p['id'] == parent_id), None)
                    if parent_task:
                        ui.icon('chevron_right', size='14px').classes('text-slate-500')
                        ui.label(f"{parent_task['title']}").classes('text-blue-300 bg-blue-900/30 px-2 py-0.5 rounded truncate max-w-[160px]')

        with ui.row().classes('w-full justify-between items-start no-wrap'):
            def on_checkbox_change(e):
                if e.value and not is_dummy:
                    database.update_task_status(t['id'], '✅ 已完成')
                    ui.notify(f'🎉 恭喜完成：「{t["title"]}」！', type='positive', position='top-right')
                    refresh_cb()
            
            is_done = (t.get('status') == '✅ 已完成')
            
            with ui.row().classes('items-center gap-2 flex-1'):
                with ui.element('div').on('click.stop', lambda e: None):
                    ui.checkbox('', value=is_done, on_change=on_checkbox_change).props('dark')
                ui.label(t.get('title', '未知任務')).classes('font-bold text-slate-100 text-lg group-hover:text-blue-400 transition-colors')

            with ui.row().classes('items-center gap-1').on('click.stop', lambda e: None):
                if t.get('status') != '✅ 已完成' and not is_dummy:
                    def quick_complete():
                        database.update_task_status(t['id'], '✅ 已完成')
                        ui.notify(f'🎉 任務【{t["title"]}】已完工！', type='positive', position='top-right')
                        refresh_cb()
                    ui.button(icon='check_circle', color='green-500', on_click=quick_complete).props('flat dense rounded').tooltip('快速標記為已完成')

        target_total = t.get('target_total', 1)
        current_progress = t.get('current_progress', 0)
        
        if target_total > 1: 
            with ui.row().classes('w-full items-center justify-between mt-1 pl-8 pr-2'):
                ui.label(f'🎯 進度: {current_progress} / {target_total}').classes('text-xs font-bold text-slate-400')
                def add_progress():
                    new_prog = current_progress + 1
                    if new_prog <= target_total:
                        database.update_task_progress(t['id'], new_prog)
                        if new_prog == target_total:
                            database.update_task_status(t['id'], '✅ 已完成')
                            ui.notify('🎉 目標達成！', type='positive', position='top-right')
                        refresh_cb()
                def minus_progress():
                    new_prog = current_progress - 1
                    if new_prog >= 0:
                        database.update_task_progress(t['id'], new_prog)
                        refresh_cb()

                if t.get('status') != '✅ 已完成':
                    with ui.row().classes('gap-1').on('click.stop', lambda e: None):
                        if current_progress > 0: ui.button('-1', on_click=minus_progress).props('outline size="sm" color="red-4" padding="xs"').classes('h-6 font-bold')
                        if current_progress < target_total: ui.button('+1', on_click=add_progress).props('outline size="sm" color="blue-4" padding="xs"').classes('h-6 font-bold')
            
            prog_ratio = current_progress / target_total if target_total > 0 else 0
            ui.linear_progress(value=prog_ratio, show_value=False).props('color="blue-5" size="4px rounded"').classes('ml-8 mt-1 w-[calc(100%-2rem)] opacity-80')

        with ui.row().classes('w-full items-center gap-4 mt-1 pl-8 text-sm text-slate-400'):
            if t.get('owner'): ui.label(f'👤 {t["owner"]}')
            if t.get('due_date'): ui.label(f'📅 {t["due_date"]}')

        with ui.row().classes('w-full justify-between items-center mt-2 pl-8'):
            with ui.row().classes('gap-2 items-center'):
                # 🌟 魔法：呼叫標籤色彩字典
                tag_name = t.get('tag')
                if not tag_name: tag_name = '一般'
                tag_color = TAG_COLORS.get(tag_name, TAG_COLORS['一般'])
                ui.label(tag_name).classes(f'text-xs px-2 py-1 rounded-md {tag_color}')
                
                det_status = t.get('detailed_status')
                if det_status: ui.label(det_status).classes('text-xs font-bold text-indigo-300 bg-indigo-900/40 border border-indigo-700/50 px-2 py-1 rounded-md shadow-sm')
            
            weight = t.get('weight', 1)
            with ui.row().classes('gap-2 items-center'):
                if weight > 1: ui.label(f'⚖️ 權重 {weight}').classes('text-xs font-bold text-amber-300 bg-amber-900/30 border border-amber-700/50 px-2 py-1 rounded-md')
                if urgent_flag: ui.label('🔥 今日急件').classes('text-xs text-red-300 font-bold bg-red-900/40 px-2 py-1 rounded-md')

        if not is_subtask and not is_dummy:
            children = [c for c in all_tasks if c.get('parent_id') == t['id'] and c.get('status') != '✅ 已完成']
            if children:
                is_expanded = t['id'] in app_state['expanded_tasks']
                def toggle_expansion(e):
                    if e.value: app_state['expanded_tasks'].add(t['id'])
                    else: app_state['expanded_tasks'].discard(t['id'])

                with ui.element('div').classes('w-full mt-3').on('click.stop', lambda e: None):
                    with ui.expansion(f'📂 展開 {len(children)} 個子任務', icon='account_tree', value=is_expanded, on_value_change=toggle_expansion).classes('w-full bg-slate-800/50 text-slate-200 rounded-lg overflow-hidden border border-slate-700'):
                        with ui.column().classes('w-full p-2 gap-0'):
                            for child in children:
                                create_rich_card(child, all_tasks, app_state, refresh_cb, is_subtask=True)

# ==========================================
# 🛠️ 模組化工具 3：月曆彩色行程標籤
# ==========================================
def create_event_badge(t, refresh_cb):
    color = 'bg-blue-600' if 'A' in t['project_name'] else ('bg-purple-600' if 'B' in t['project_name'] else 'bg-orange-600')
    if t['status'] == '✅ 已完成': color = 'bg-slate-600 line-through text-slate-400'
    badge = ui.label(t['title']).classes(f'text-xs text-white px-2 py-1 rounded truncate cursor-pointer {color} hover:opacity-80 transition-opacity w-full shadow-sm')
    badge.on('click', lambda: open_task_detail_modal(t, refresh_cb))

# ==========================================
# 🛠️ 模組化工具 4：新增任務彈出視窗 
# ==========================================
# 🌟 修正 1：參數加上 current_year 預設值
def open_new_task_dialog(project_list, refresh_cb, default_parent_id='', default_project='', current_year=115):
    all_t = database.get_all_tasks()
    options = {'': '👑 本身為獨立大任務 (無爸爸)'}
    for t in all_t:
        if t['status'] != '✅ 已完成':
            options[t['id']] = f"[{t['project_name'][:4]}] {t['title']}"

    with ui.dialog() as new_task_dialog, ui.card().classes('w-[600px] p-6 rounded-2xl shadow-2xl'):
        ui.label('✨ 新增戰略任務').classes('text-xl font-extrabold text-blue-400 mb-4')
        
        # 🌟 修正 2：加入「執行年度」下拉選單，並與任務名稱排在同一行
        with ui.row().classes('w-full gap-2 no-wrap mb-2'):
            year_input = ui.select([113, 114, 115, 116], label='📅 執行年度', value=current_year).classes('w-1/4').props('dark outlined')
            task_name = ui.input('任務名稱 / 查核點').classes('w-3/4').props('dark outlined')
            
        with ui.row().classes('w-full gap-2 no-wrap'):
            val_proj = default_project if default_project in project_list else (project_list[0] if project_list else '')
            project_select = ui.select(project_list, label='所屬專案', value=val_proj).classes('w-1/2').props('dark outlined')
            tag_select = ui.select(['行政作業', '數據處理', '現場會勘', '追蹤日誌', '活動辦理', '一般', '其他'], label='任務標籤', value='行政作業').classes('w-1/2').props('dark outlined')

        with ui.row().classes('w-full gap-2 no-wrap mt-2'):
            # 🌟 完美平衡：換回下拉選單，並在 Label 加上溫馨提示
            owner_list = list(set([task['owner'] for task in all_t if task.get('owner')]))
            if '未指定' not in owner_list: owner_list.insert(0, '未指定')
            
            owner_input = ui.select(owner_list, label='👤 主責人員 (新名字請按 Enter)', value='未指定', with_input=True, new_value_mode='add-unique').classes('w-1/2').props('dark outlined')
            due_date_input = ui.input('📅 預計完成日').props('type="date" dark outlined').classes('w-1/2')

        with ui.row().classes('w-full gap-2 no-wrap mt-2 items-center bg-slate-800/60 p-3 rounded-lg border border-slate-700'):
            weight_input = ui.number('⚖️ 任務權重', value=1, min=1).classes('w-1/4').props('dark outlined')
            target_input = ui.number('🎯 目標總數', value=1, min=1).classes('w-1/4').props('dark outlined')
            
            # 🛡️ 爸爸 ID 防呆
            p_val = default_parent_id if default_parent_id in options else ''
            parent_select = ui.select(options, label='📂 歸屬大項目 (可選)', value=p_val).classes('w-1/2').props('dark outlined')

        with ui.row().classes('w-full gap-2 no-wrap mt-3 items-center'):
            detailed_status_select = ui.select(['規劃中', '待追蹤', '追蹤狀況', '執行中', '卡關'], label='🔍 細部追蹤狀態', value='規劃中').classes('w-2/3').props('dark outlined')
            is_urgent = ui.checkbox('🔥 今日急件').classes('text-red-400 font-bold w-1/3 mt-2').props('dark')

        vendor_notes_input = ui.textarea('🏢 追蹤日誌').classes('w-full mt-2').props('dark outlined')
        ui.separator().classes('my-4 border-slate-700')
        
        def save_to_db():
            if not task_name.value:
                ui.notify('請輸入任務名稱！', type='warning')
                return
            p_id = parent_select.value if parent_select.value != '' else None
            database.add_task(
                project_name=project_select.value, title=task_name.value, tag=tag_select.value,
                owner=owner_input.value, due_date=due_date_input.value, status='📋 待辦事項',
                detailed_status=detailed_status_select.value, vendor_and_notes=vendor_notes_input.value,
                is_urgent=1 if is_urgent.value else 0, parent_id=p_id,
                weight=int(weight_input.value), target_total=int(target_input.value), current_progress=0,
                year=year_input.value # 🌟 修正 3：把選定的年度傳給資料庫！
            )
            ui.notify(f'✅ 已成功寫入資料庫！', type='positive', position='top-right')
            new_task_dialog.close()
            refresh_cb() 

        with ui.row().classes('w-full justify-end gap-2'):
            ui.button('取消', on_click=new_task_dialog.close, color='slate-600').props('flat')
            ui.button('💾 寫入大腦', on_click=save_to_db).props('rounded color="primary"')
            
    new_task_dialog.open()