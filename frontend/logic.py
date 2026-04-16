import streamlit as st
import pandas as pd
from datetime import datetime
from backend.core import fetch_power_outage_schedule, parse_schedule, is_highlight_area

def fetch_data():
    """
    Fetches schedule data without displaying UI elements.
    Returns (success, count)
    """
    try:
        html = fetch_power_outage_schedule()
        if html:
            schedules = parse_schedule(html)
            st.session_state.schedules = schedules
            st.session_state.last_updated = datetime.now()
            return True, len(schedules)
        return False, 0
    except Exception:
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
