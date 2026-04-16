import streamlit as st
from datetime import datetime
import pandas as pd

# Update path to find backend
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core import PROVINCE_NAME, get_highlight_areas_display
from frontend.styles import get_theme, apply_custom_css
from frontend.logic import fetch_data, schedules_to_df, apply_filters
from frontend.components.table import render_table

# =============================================================
# PAGE CONFIG
# =============================================================
st.set_page_config(
    page_title=f"Lịch Cúp Điện – {PROVINCE_NAME}",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# SESSION STATE
# =============================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False 
if "schedules" not in st.session_state:
    st.session_state.schedules = []
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "auto_loaded" not in st.session_state:
    st.session_state.auto_loaded = False
if "toast_queue" not in st.session_state:
    st.session_state.toast_queue = []


# =============================================================
# THEME & CSS
# =============================================================
T = get_theme(st.session_state.dark_mode)
apply_custom_css(T)

# Show pending toasts
for toast_msg, toast_icon in st.session_state.toast_queue:
    st.toast(toast_msg, icon=toast_icon)
st.session_state.toast_queue = []

# =============================================================
# SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown(f'<div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔌</div>', unsafe_allow_html=True)
    st.markdown(f"### Lịch Cúp Điện\n**{PROVINCE_NAME}**")
    
    # Dark / Light mode icon button
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        if st.button(T["toggle_icon"], key="toggle_theme", help=T["toggle_tip"]):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    
    # Stats card in sidebar
    if st.session_state.schedules:
        df_all = schedules_to_df(st.session_state.schedules)
        total_all = len(df_all)
        xt_all = len(df_all[df_all["_hl"]])
        
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 0.8rem; background: {T['bg_card']};">
            <div class="stat-value" style="font-size: 1.5rem;">{total_all}</div>
            <div class="stat-label">Tổng lịch</div>
        </div>
        <div class="stat-card" style="margin-bottom: 0.8rem; background: {T['bg_card']};">
            <div class="stat-value" style="font-size: 1.5rem; color: {T['emerald_light']};">{xt_all}</div>
            <div class="stat-label">Xuân Trường</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_updated:
            st.markdown(f"<small>🕒 Cập nhật: {st.session_state.last_updated.strftime('%d/%m/%Y %H:%M')}</small>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top: 2rem; font-size: 0.7rem; opacity: 0.6;">
        Nguồn: <a href="https://lichcupdien.org" target="_blank" style="color: inherit;">lichcupdien.org</a>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# MAIN UI
# =============================================================
# Auto load data once
if not st.session_state.auto_loaded:
    with st.status("🔍 Đang đồng bộ dữ liệu...", expanded=False) as status:
        success, count = fetch_data()
        st.session_state.auto_loaded = True
        if success:
            status.update(label=f"Đã tải {count} lịch cúp điện", state="complete", expanded=False)
            st.session_state.toast_queue.append((f"Đã cập nhật {count} lịch cúp điện!", "⚡"))
            st.rerun()
        else:
            status.update(label="Không thể tải dữ liệu", state="error", expanded=False)

# ── Filter panel ──────────────
st.markdown('<div class="filter-panel main-area">', unsafe_allow_html=True)
st.markdown('<div class="filter-label">⚡ BỘ LỌC</div>', unsafe_allow_html=True)

f_col1, f_col2, f_col_right = st.columns([3, 4, 3])

with f_col1:
    all_dien_luc = sorted(list(set(s.get("dien_luc", "") for s in st.session_state.schedules))) if st.session_state.schedules else []
    sel_dien_luc = st.multiselect("Điện Lực", options=all_dien_luc, placeholder="Tất cả điện lực...", label_visibility="collapsed")

with f_col2:
    khu_vuc_text = st.text_input("Khu Vực", placeholder="Lọc theo khu vực...", label_visibility="collapsed")

with f_col_right:
    c1, c2 = st.columns([5, 2])
    with c1:
        highlight_only = st.checkbox("📍 Xuân Trường", value=False, help=f"Chỉ hiện các địa điểm thuộc: {get_highlight_areas_display()}")
    with c2:
        if st.button("🔄", help="Lấy lịch cúp điện mới nhất"):
            with st.status("", expanded=False) as status:
                success, count = fetch_data()
                if success:
                    st.session_state.toast_queue.append((f"Đã cập nhật {count} lịch cúp điện!", "✅"))
                else:
                    st.session_state.toast_queue.append(("Lỗi khi tải dữ liệu mới!", "❌"))
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Stats bar ──────────────
if st.session_state.schedules:
    df_raw = schedules_to_df(st.session_state.schedules)
    df_filtered, f_schedules = apply_filters(df_raw, st.session_state.schedules, "", sel_dien_luc, khu_vuc_text, highlight_only)
    
    total = len(df_filtered)
    xt_count = len(df_filtered[df_filtered["_hl"]])
    dl_count = len(df_filtered["Điện Lực"].unique()) if total > 0 else 0
    
    st.markdown(f"""
    <div class="stats-bar main-area">
        <div class="stat-card">
            <div class="stat-value">{total}</div>
            <div class="stat-label">Hiển thị</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: {T['emerald_light']};">{xt_count}</div>
            <div class="stat-label">Xuân Trường</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{dl_count}</div>
            <div class="stat-label">Điện Lực</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Data Table ──────────────
    if not df_filtered.empty:
        render_table(df_filtered, T)
    else:
        st.markdown(f"""
        <div class="empty-box main-area">
            <div class="ei">🔍</div>
            <div class="et">Không tìm thấy lịch cúp điện</div>
            <div class="es">Vui lòng điều chỉnh bộ lọc hoặc nhấn 🔄 để cập nhật lại dữ liệu.</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──────────────
st.markdown(f"""
<div class="app-footer main-area">
    <div>&copy; {datetime.now().year} <b>Lịch Cúp Điện {PROVINCE_NAME}</b></div>
    <div>Sử dụng dữ liệu từ <a href="https://lichcupdien.org" class="footer-link">lichcupdien.org</a></div>
</div>
""", unsafe_allow_html=True)
