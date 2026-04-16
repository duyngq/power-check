import streamlit as st

def get_theme(is_dark):
    if is_dark:
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

def apply_custom_css(T):
    css = f"""
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

    /* Hiện lại header và sidebar mặc định để đảm bảo nút toggle hoạt động */
    #[data-testid="stHeader"] {{ visibility: visible !important; display: flex !important; background: transparent !important; }}
    [data-testid="stSidebar"] {{ 
        visibility: visible !important; 
        background: {T['bg_sidebar']} !important;
        border-right: 1px solid {T['border']} !important;
    }}

    /* ── Sidebar Button Fix (Theme toggle) ──────────────── */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] button {{
        padding: 0 !important;
        min-height: 2.5rem !important;
        width: 2.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] button p {{
        font-size: 1.2rem !important;
        margin: 0 !important;
    }}

    /* ── Sidebar scroll & control ────────────────────────── */
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
    """
    st.markdown(css, unsafe_allow_html=True)
