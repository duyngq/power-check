"""
Streamlit Web UI – Lịch Cúp Điện Dashboard (v2)
REQ-003 v2: Sidebar, sortable table, pagination, icon-only dark toggle
Chạy: streamlit run streamlit_app.py
"""

import sys
import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime

# st.iframe replaces deprecated API but doesn't support scrolling;
# use st.components.v1.html for standalone HTML rendering.
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(__file__))

from core import (
    PROVINCE_NAME,
    POWER_OUTAGE_URL,
    HIGHLIGHT_AREAS,
    fetch_power_outage_schedule,
    parse_schedule,
    is_highlight_area,
    get_highlight_areas_display,
)

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
    st.session_state.dark_mode = False  # Light mode by default
if "schedules" not in st.session_state:
    st.session_state.schedules = []
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
# Guard: auto_loaded resets each browser session, not Streamlit rerun
if "auto_loaded" not in st.session_state:
    st.session_state.auto_loaded = False

# =============================================================
# THEME
# =============================================================
def get_theme():
    if st.session_state.dark_mode:
        return {
            "bg_page":        "#0f172a",
            "bg_card":        "#1e293b",
            "bg_card2":       "#162032",
            "bg_sidebar":     "#0d1f2d",
            "bg_table_head":  "#134e3a",
            "bg_table_even":  "#1a2e40",
            "bg_table_odd":   "#1e293b",
            "bg_highlight":   "rgba(16,185,129,0.18)",
            "bg_input":       "#1e293b",
            "border":         "#2d4a61",
            "border_hl":      "#10b981",
            "text_primary":   "#f1f5f9",
            "text_secondary": "#94a3b8",
            "emerald":        "#10b981",
            "emerald_hover":  "#059669",
            "emerald_light":  "#34d399",
            "stat_bg":        "#134e3a",
            "badge_bg":       "rgba(16,185,129,0.2)",
            "shadow":         "0 4px 24px rgba(0,0,0,0.4)",
            "pg_active_bg":   "#10b981",
            "pg_active_fg":   "#ffffff",
            "pg_bg":          "#1e293b",
            "pg_fg":          "#94a3b8",
            "pg_border":      "#2d4a61",
            "toggle_icon":    "☀️",
            "toggle_tip":     "Chuyển Light Mode",
        }
    else:
        return {
            "bg_page":        "#f0fdf4",
            "bg_card":        "#ffffff",
            "bg_card2":       "#f0fdf4",
            "bg_sidebar":     "#dcfce7",
            "bg_table_head":  "#d1fae5",
            "bg_table_even":  "#f9fafb",
            "bg_table_odd":   "#ffffff",
            "bg_highlight":   "rgba(16,185,129,0.10)",
            "bg_input":       "#ffffff",
            "border":         "#d1fae5",
            "border_hl":      "#10b981",
            "text_primary":   "#111827",
            "text_secondary": "#6b7280",
            "emerald":        "#059669",
            "emerald_hover":  "#047857",
            "emerald_light":  "#10b981",
            "stat_bg":        "#d1fae5",
            "badge_bg":       "rgba(16,185,129,0.15)",
            "shadow":         "0 4px 24px rgba(0,0,0,0.08)",
            "pg_active_bg":   "#059669",
            "pg_active_fg":   "#ffffff",
            "pg_bg":          "#ffffff",
            "pg_fg":          "#6b7280",
            "pg_border":      "#d1fae5",
            "toggle_icon":    "🌙",
            "toggle_tip":     "Chuyển Dark Mode",
        }

T = get_theme()

# =============================================================
# GLOBAL CSS
# =============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
/* Chỉ áp dụng font Inter cho các khối nội dung của dashboard */
.main-area, .filter-panel, .stat-card, .app-footer, [data-testid="stMarkdownContainer"] p {{ 
    font-family: 'Inter', sans-serif !important; 
}}

/* Đảm bảo Sidebar title và các văn bản khác dùng font Inter nhưng không chạm vào Icon */
[data-testid="stSidebar"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{ background: {T['bg_page']} !important; color: {T['text_primary']} !important; }}
#MainMenu, footer {{ visibility: hidden; }}

/* Hiện lại header và sidebar */
[data-testid="stHeader"] {{ visibility: visible !important; display: flex !important; background: transparent !important; }}
[data-testid="stSidebar"] {{ 
    visibility: visible !important; 
    background: {T['bg_sidebar']} !important;
    border-right: 1px solid {T['border']} !important;
}}

/* Ẩn thanh cuộn của Sidebar */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] > div:first-child {{
    overflow: hidden !important;
}}

/* Đảm bảo nút đóng/mở sidebar hiển thị rõ ràng */
[data-testid="collapsedControl"] {{
    color: {T['text_primary']} !important;
}}

/* ── Filter panel ────────────────────────────────────── */
.filter-panel {{
    background: {T['bg_card2']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 0.8rem 1.2rem 0.5rem 1.2rem;
    margin-bottom: 0.8rem;
}}
.filter-label {{
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.8px;
    color: {T['emerald_light']}; margin-bottom: 0.4rem;
}}
div[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
    background: {T['bg_input']} !important;
    border-color: {T['border']} !important;
    color: {T['text_primary']} !important;
    border-radius: 8px !important;
}}
div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{
    background: {T['badge_bg']} !important;
    color: {T['emerald_light']} !important;
}}
div[data-testid="stCheckbox"] label {{
    color: {T['text_primary']} !important;
    font-size: 0.875rem !important;
}}

/* ── Stats bar ───────────────────────────────────────── */
.stats-bar {{
    display: flex; gap: 0.8rem; margin-bottom: 0.8rem; flex-wrap: wrap;
}}
.stat-card {{
    flex: 1; min-width: 130px;
    background: {T['stat_bg']};
    border: 1px solid {T['border_hl']};
    border-radius: 12px; padding: 0.8rem 1rem; text-align: center;
}}
.stat-value {{ font-size: 1.9rem; font-weight: 800; color: {T['emerald_light']}; line-height: 1; }}
.stat-label {{ font-size: 0.68rem; font-weight: 600; color: {T['text_secondary']}; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.5px; }}

/* ── Empty state ─────────────────────────────────────── */
.empty-box {{
    background: {T['bg_card']}; border: 1px solid {T['border']};
    border-radius: 14px; padding: 3rem 2rem; text-align: center;
    color: {T['text_secondary']};
}}
.empty-box .ei {{ font-size: 2.8rem; margin-bottom: 0.6rem; }}
.empty-box .et {{ font-size: 1rem; font-weight: 600; color: {T['text_primary']}; margin-bottom: 0.3rem; }}
.empty-box .es {{ font-size: 0.83rem; }}

/* ── Footer ──────────────────────────────────────────── */
.app-footer {{
    margin-top: 0.5rem; padding: 0.7rem 1rem;
    background: {T['bg_card2']}; border: 1px solid {T['border']};
    border-radius: 10px; display: flex;
    justify-content: space-between; align-items: center;
    font-size: 0.74rem; color: {T['text_secondary']}; flex-wrap: wrap; gap: 0.4rem;
}}
.footer-link {{ color: {T['emerald_light']}; text-decoration: none; font-weight: 500; }}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {T['bg_card2']}; }}
::-webkit-scrollbar-thumb {{ background: {T['emerald_hover']}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)


# =============================================================
# HELPERS
# =============================================================
def fetch_data():
    with st.spinner("⏳ Đang tải lịch cúp điện..."):
        html = fetch_power_outage_schedule()
        if html:
            schedules = parse_schedule(html)
            st.session_state.schedules = schedules
            st.session_state.last_updated = datetime.now()
            return True, len(schedules)
        return False, 0


def schedules_to_df(schedules: list) -> pd.DataFrame:
    if not schedules:
        return pd.DataFrame()
    rows = []
    for idx, s in enumerate(schedules, 1):
        rows.append({
            "#":           idx,
            "Điện Lực":   s.get("dien_luc", ""),
            "Ngày":        s.get("ngay", ""),
            "Thời Gian":  s.get("thoi_gian", ""),
            "Khu Vực":    s.get("khu_vuc", ""),
            "Lý Do":       s.get("ly_do", ""),
            "Trạng Thái": s.get("trang_thai", ""),
            "_hl":         is_highlight_area(s.get("khu_vuc", "")),
        })
    return pd.DataFrame(rows)


def apply_filters(df, schedules, search, sel_dien_luc, khu_vuc_text, highlight_only):
    if df.empty:
        return df, schedules
    mask = pd.Series([True] * len(df), index=df.index)
    if search.strip():
        q = search.strip().lower()
        mask &= df.apply(lambda r: q in " ".join(str(v) for v in r.values).lower(), axis=1)
    if sel_dien_luc:
        mask &= df["Điện Lực"].isin(sel_dien_luc)
    if khu_vuc_text.strip():
        mask &= df["Khu Vực"].str.contains(khu_vuc_text.strip(), case=False, na=False)
    if highlight_only:
        mask &= df["_hl"]
    filtered = df[mask].copy()
    filtered["#"] = range(1, len(filtered) + 1)
    f_schedules = [schedules[i] for i in mask[mask].index.tolist()] if not filtered.empty else []
    return filtered, f_schedules


def build_table_iframe(df: pd.DataFrame, theme: dict, page_size: int = 20) -> str:
    """
    Standalone HTML với JS sort + pagination để dùng với st.iframe.
    Tất cả rows được nhúng dưới dạng JSON, JS render theo page.
    """
    T = theme

    # Build JSON rows (bỏ cột _hl dùng trong Python)
    cols_display = ["#", "Điện Lực", "Ngày", "Thời Gian", "Khu Vực", "Lý Do", "Trạng Thái"]
    rows_json = []
    for _, row in df.iterrows():
        rows_json.append({
            "idx":      str(row["#"]),
            "dien_luc": str(row["Điện Lực"]),
            "ngay":     str(row["Ngày"]),
            "tg":       str(row["Thời Gian"]),
            "khu_vuc":  str(row["Khu Vực"]),
            "ly_do":    str(row["Lý Do"]),
            "tt":       str(row["Trạng Thái"]),
            "hl":       bool(row["_hl"]),
        })

    rows_json_str = json.dumps(rows_json, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}}
body{{background:{T['bg_card']};color:{T['text_primary']};font-size:13.5px;}}
/* ── Table ── */
.wrap{{overflow-x:auto;width:100%;}}
table{{width:100%;border-collapse:collapse;}}
thead th{{
  padding:10px 12px;text-align:left;font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.7px;color:{T['emerald']};
  background:{T['bg_table_head']};border-bottom:2px solid {T['border_hl']};
  white-space:nowrap;cursor:pointer;user-select:none;position:relative;
}}
thead th:hover{{opacity:.85;}}
thead th.center{{text-align:center;}}
thead th .sort-arr{{margin-left:4px;font-size:10px;opacity:.5;}}
thead th.asc  .sort-arr::after{{content:'▲';opacity:1;}}
thead th.desc .sort-arr::after{{content:'▼';opacity:1;}}
thead th .sort-arr::after{{content:'⇅';}}
tbody tr{{border-bottom:1px solid {T['border']};transition:background .12s;}}
tbody tr:nth-child(even){{background:{T['bg_table_even']};}}
tbody tr:nth-child(odd){{background:{T['bg_table_odd']};}}
tbody tr:hover{{background:{T['badge_bg']} !important;}}
tbody tr.hl{{background:{T['bg_highlight']} !important;border-left:3px solid {T['border_hl']};}}
tbody tr.hl:hover{{background:rgba(16,185,129,.28) !important;}}
td{{padding:9px 12px;vertical-align:top;line-height:1.45;color:{T['text_primary']};}}
td.center{{text-align:center;}}
.badge-hl{{
  display:inline-block;background:{T['badge_bg']};color:{T['emerald_light']};
  border:1px solid {T['emerald']};border-radius:20px;font-size:10.5px;
  font-weight:600;padding:1px 7px;margin-left:5px;vertical-align:middle;
}}
.badge-tt{{
  display:inline-block;background:rgba(16,185,129,.15);color:{T['emerald_light']};
  border-radius:20px;font-size:11px;font-weight:600;padding:2px 9px;
}}
/* ── Pagination ── */
.pg-bar{{
  display:flex;align-items:center;justify-content:space-between;
  padding:10px 14px;background:{T['bg_card2']};border-top:1px solid {T['border']};
  flex-wrap:wrap;gap:6px;
}}
.pg-info{{font-size:11.5px;color:{T['text_secondary']};}}
.pg-btns{{display:flex;gap:4px;align-items:center;flex-wrap:wrap;}}
button.pg{{
  border:1px solid {T['pg_border']};background:{T['pg_bg']};color:{T['pg_fg']};
  border-radius:6px;padding:4px 9px;font-size:12px;cursor:pointer;
  font-family:'Inter',sans-serif;transition:all .15s;
}}
button.pg:hover{{border-color:{T['emerald']};color:{T['emerald']};}}
button.pg.active{{background:{T['pg_active_bg']};color:{T['pg_active_fg']};border-color:{T['pg_active_bg']};font-weight:600;}}
button.pg:disabled{{opacity:.4;cursor:not-allowed;}}
.pg-jump{{display:flex;align-items:center;gap:6px;font-size:11.5px;color:{T['text_secondary']};}}
.pg-jump input{{
  width:44px;padding:3px 5px;border:1px solid {T['border']};border-radius:5px;
  background:{T['bg_input']};color:{T['text_primary']};font-size:12px;text-align:center;
}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:{T['bg_card2']};}}
::-webkit-scrollbar-thumb{{background:{T['emerald_hover']};border-radius:3px;}}
</style>
</head>
<body>
<div id="pg-top" class="pg-bar"></div>
<div class="wrap">
<table id="tbl">
<thead id="thead">
<tr>
  <th class="center" data-col="idx" data-type="num"># <span class="sort-arr"></span></th>
  <th data-col="dien_luc">Điện Lực <span class="sort-arr"></span></th>
  <th class="center" data-col="ngay">Ngày <span class="sort-arr"></span></th>
  <th class="center" data-col="tg">Thời Gian <span class="sort-arr"></span></th>
  <th data-col="khu_vuc">Khu Vực <span class="sort-arr"></span></th>
  <th data-col="ly_do">Lý Do <span class="sort-arr"></span></th>
  <th class="center" data-col="tt">Trạng Thái <span class="sort-arr"></span></th>
</tr>
</thead>
<tbody id="tbody"></tbody>
</table>
</div>
<div id="pg-bot" class="pg-bar"></div>

<script>
const PAGE_SIZE = {page_size};
const allData  = {rows_json_str};

let sortCol = null;
let sortDir = 1;   // 1=asc -1=desc
let curPage = 0;

function sortedData() {{
  if (!sortCol) return [...allData];
  return [...allData].sort((a, b) => {{
    let av = a[sortCol], bv = b[sortCol];
    const th = document.querySelector(`[data-col="${{sortCol}}"]`);
    if (th && th.dataset.type === 'num') {{
      av = parseFloat(av) || 0; bv = parseFloat(bv) || 0;
    }} else {{
      av = av.toLowerCase(); bv = bv.toLowerCase();
    }}
    return av < bv ? -sortDir : av > bv ? sortDir : 0;
  }});
}}

function escHtml(s) {{
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function renderTable() {{
  const data   = sortedData();
  const total  = data.length;
  const pages  = Math.max(1, Math.ceil(total / PAGE_SIZE));
  if (curPage >= pages) curPage = pages - 1;

  const start  = curPage * PAGE_SIZE;
  const slice  = data.slice(start, start + PAGE_SIZE);

  // rows
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = slice.map(r => {{
    const hlClass = r.hl ? ' class="hl"' : '';
    let kv = escHtml(r.khu_vuc);
    if (r.hl) kv += ' <span class="badge-hl">📍 Theo dõi</span>';
    return `<tr${{hlClass}}>
      <td class="center">${{escHtml(r.idx)}}</td>
      <td><strong>${{escHtml(r.dien_luc)}}</strong></td>
      <td class="center">${{escHtml(r.ngay)}}</td>
      <td class="center">${{escHtml(r.tg)}}</td>
      <td>${{kv}}</td>
      <td>${{escHtml(r.ly_do)}}</td>
      <td class="center"><span class="badge-tt">${{escHtml(r.tt)}}</span></td>
    </tr>`;
  }}).join('');

  // pagination bars
  const info = `Hiển thị <strong>${{start+1}}–${{Math.min(start+PAGE_SIZE,total)}}</strong> / ${{total}} lịch`;
  [document.getElementById('pg-top'), document.getElementById('pg-bot')].forEach(bar => {{
    bar.innerHTML = `
      <div class="pg-info">${{info}}</div>
      <div class="pg-btns">
        <button class="pg" onclick="goPage(0)" ${{curPage===0?'disabled':''}}>«</button>
        <button class="pg" onclick="goPage(${{curPage-1}})" ${{curPage===0?'disabled':''}}>‹</button>
        ${{pageButtons(pages)}}
        <button class="pg" onclick="goPage(${{curPage+1}})" ${{curPage>=pages-1?'disabled':''}}>›</button>
        <button class="pg" onclick="goPage(${{pages-1}})" ${{curPage>=pages-1?'disabled':''}}>»</button>
      </div>
      <div class="pg-jump">
        Trang
        <input type="number" min="1" max="${{pages}}" value="${{curPage+1}}"
          onchange="goPage(parseInt(this.value)-1)"
          onkeydown="if(event.key==='Enter')goPage(parseInt(this.value)-1)">
        / ${{pages}}
      </div>`;
  }});

  // sort arrows
  document.querySelectorAll('thead th').forEach(th => {{
    th.classList.remove('asc','desc');
    if (th.dataset.col === sortCol) th.classList.add(sortDir===1?'asc':'desc');
  }});
}}

function pageButtons(pages) {{
  const MAX_BTN = 7;
  let btns = [];
  if (pages <= MAX_BTN) {{
    for (let i=0;i<pages;i++) btns.push(i);
  }} else {{
    let left = Math.max(0, curPage-2);
    let right = Math.min(pages-1, curPage+2);
    if (curPage < 3) right = 4;
    if (curPage > pages-4) left = pages-5;
    if (left > 0) {{ btns.push(0); if(left>1) btns.push('...'); }}
    for(let i=left;i<=right;i++) btns.push(i);
    if (right < pages-1) {{ if(right<pages-2) btns.push('...'); btns.push(pages-1); }}
  }}
  return btns.map(b => b==='...'
    ? `<span style="color:{T['text_secondary']};padding:0 2px;">…</span>`
    : `<button class="pg${{b===curPage?' active':''}}" onclick="goPage(${{b}})">${{b+1}}</button>`
  ).join('');
}}

function goPage(p) {{
  const pages = Math.max(1, Math.ceil(allData.length / PAGE_SIZE));
  curPage = Math.max(0, Math.min(p, pages-1));
  renderTable();
  window.scrollTo(0,0);
}}

// Sort on header click
document.querySelectorAll('thead th[data-col]').forEach(th => {{
  th.addEventListener('click', () => {{
    const col = th.dataset.col;
    if (sortCol === col) {{ sortDir *= -1; }}
    else {{ sortCol = col; sortDir = 1; }}
    curPage = 0;
    renderTable();
  }});
}});

renderTable();
</script>
</body>
</html>"""


# =============================================================
# AUTO LOAD
# =============================================================
if not st.session_state.auto_loaded:
    st.session_state.auto_loaded = True
    ok, count = fetch_data()
    if not ok:
        st.warning("⚠️ Không thể tải dữ liệu. Nhấn **'⟳ Lấy lịch mới nhất'** để thử lại.")


# =============================================================
# ── SIDEBAR ────────────────────────────────────────────────
# =============================================================
with st.sidebar:
    # App logo + title
    st.markdown(f"""
    <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
      <div style="font-size:2.8rem; margin-bottom:0.3rem;">🔌</div>
      <div style="font-size:1.05rem; font-weight:800; color:{T['emerald_light']}; line-height:1.2;">
        Lịch Cúp Điện
      </div>
      <div style="font-size:0.88rem; font-weight:700; color:{T['text_primary']}; margin-top:2px;">
        {PROVINCE_NAME}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Dark / Light mode — icon only button, centered
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        if st.button(T["toggle_icon"], key="toggle_theme", help=T["toggle_tip"]):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    border_col = T['border']
    st.markdown(f"<hr style='border-color:{border_col};margin:0.8rem 0;'>", unsafe_allow_html=True)

    # Info box
    updated_str = (
        st.session_state.last_updated.strftime("%d/%m/%Y %H:%M")
        if st.session_state.last_updated else "Chưa cập nhật"
    )
    total_schedules = len(st.session_state.schedules)
    hl_total = sum(1 for s in st.session_state.schedules if is_highlight_area(s.get("khu_vuc", "")))

    st.markdown(f"""
    <div style="font-size:0.75rem; color:{T['text_secondary']}; line-height:2;">
      <div>📊 Tổng lịch: <strong style="color:{T['emerald_light']}">{total_schedules}</strong></div>
      <div>📍 Xuân Trường: <strong style="color:#f59e0b">{hl_total}</strong></div>
      <div>🕐 Cập nhật: <strong style="color:{T['text_primary']}">{updated_str}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{T['border']};margin:0.8rem 0;'>", unsafe_allow_html=True)

    st.markdown(
        f"<div style='font-size:0.68rem;color:{T['text_secondary']};'>Nguồn: "
        f"<a href='{POWER_OUTAGE_URL}' target='_blank' style='color:{T['emerald_light']};'>"
        f"lichcupdien.org</a></div>",
        unsafe_allow_html=True,
    )


# =============================================================
# ── MAIN AREA ──────────────────────────────────────────────
# =============================================================
st.markdown('<div class="main-area">', unsafe_allow_html=True)

# search_query removed — search moved out of main area
search_query = ""

# ── Filter panel ─────────────────────────────────────────────
schedules = st.session_state.schedules
df_all = schedules_to_df(schedules)
dien_luc_options = sorted(df_all["Điện Lực"].unique().tolist()) if not df_all.empty else []

#st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown('<div class="filter-label">⚡ Bộ lọc</div>', unsafe_allow_html=True)

f_col1, f_col2, f_col_right = st.columns([4, 4, 2])

with f_col1:
    sel_dien_luc = st.multiselect(
        "Điện Lực",
        options=dien_luc_options,
        default=[],
        placeholder="Tất cả điện lực...",
        key="filter_dien_luc",
    )
with f_col2:
    khu_vuc_text = st.text_input(
        "Khu Vực",
        placeholder="Lọc theo khu vực...",
        key="filter_khu_vuc",
    )
with f_col_right:
    # Checkbox + Refresh cạnh nhau, compact, canh phải
    rc1, rc2 = st.columns([2, 2])
    with rc1:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        highlight_only = st.checkbox(
            "",
            key="filter_highlight_only",
            label_visibility="visible",
            help="Chỉ hiện lịch cúp điện tại khu vực Xuân Trường",
        )
    with rc2:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        refresh_clicked = st.button(
            "🔄",
            key="btn_refresh",
            help="Lấy lịch cúp điện mới nhất từ lichcupdien.org",
        )

st.markdown("</div>", unsafe_allow_html=True)

# Handle refresh
if refresh_clicked:
    ok, count = fetch_data()
    if ok:
        st.toast(f"✅ Đã tải {count} lịch cúp điện!", icon="✅")
    else:
        st.error("❌ Không thể kết nối đến lichcupdien.org. Vui lòng thử lại sau.")
    st.rerun()

# ── Apply filters ─────────────────────────────────────────────
filtered_df, filtered_schedules = apply_filters(
    df_all, schedules,
    search_query,
    sel_dien_luc,
    khu_vuc_text,
    highlight_only,
)

highlight_count = filtered_df["_hl"].sum() if not filtered_df.empty else 0
total_count     = len(filtered_df)
dien_luc_count  = df_all["Điện Lực"].nunique() if not df_all.empty else 0
updated_str_main = (
    st.session_state.last_updated.strftime("%H:%M")
    if st.session_state.last_updated else "--:--"
)

# ── Stats bar (3 cards – removed "Cập nhật lúc") ─────────────
st.markdown(f"""
<div class="stats-bar">
  <div class="stat-card">
    <div class="stat-value">{total_count}</div>
    <div class="stat-label">Hiển thị</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#f59e0b">{highlight_count}</div>
    <div class="stat-label">Xuân Trường</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" style="color:#60a5fa">{dien_luc_count}</div>
    <div class="stat-label">Điện Lực</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Data table (iframe with JS sort + pagination) ─────────────
if filtered_df.empty:
    msg = (
        ("⟳ Lấy lịch mới nhất", "Chưa có dữ liệu", "📭")
        if df_all.empty
        else ("điều chỉnh bộ lọc", "Không tìm thấy kết quả", "🔍")
    )
    st.markdown(f"""
    <div class="empty-box">
      <div class="ei">{msg[2]}</div>
      <div class="et">{msg[1]}</div>
      <div class="es">Nhấn <strong>"{msg[0]}"</strong> để thử lại</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Tính height: max 20 rows × 47px + header 44px + 2×pagination 52px + buffer
    rows_shown  = min(len(filtered_df), 20)
    table_h     = 44 + rows_shown * 47 + 52 * 2 + 16
    table_html  = build_table_iframe(filtered_df, T, page_size=20)
    components.html(table_html, height=table_h)

# ── Footer ────────────────────────────────────────────────────
active_filters = []
if sel_dien_luc:            active_filters.append(f"Điện lực: {', '.join(sel_dien_luc)}")
if khu_vuc_text.strip():    active_filters.append(f'Khu vực: "{khu_vuc_text.strip()}"')
if highlight_only:          active_filters.append("Chỉ khu vực theo dõi")
filter_str = " · ".join(active_filters) if active_filters else "Không có bộ lọc"

st.markdown(f"""
<div class="app-footer">
  <div>🔽 Lọc: {filter_str}</div>
  <div>Nguồn: <a class="footer-link" href="{POWER_OUTAGE_URL}" target="_blank">lichcupdien.org</a></div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # .main-area