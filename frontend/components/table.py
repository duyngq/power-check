import json
import pandas as pd

def build_table_iframe(df: pd.DataFrame, theme: dict, page_size: int = 20) -> str:
    """
    Standalone HTML với JS sort + pagination để dùng với st.iframe.
    """
    T = theme

    # Build JSON rows
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
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}}
body{{background:{T['bg_card']};color:{T['text_primary']};font-size:13.5px;}}
/* ── Table ── */
.wrap{{overflow-x:auto;width:100%;-webkit-overflow-scrolling:touch;}}
table{{width:100%;border-collapse:collapse;}}
thead th{{
  padding:10px 12px;text-align:left;font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.7px;color:{T['emerald']};
  background:{T['bg_table_head']};border-bottom:2px solid {T['border_hl']};
  white-space:nowrap;cursor:pointer;user-select:none;position:relative;
}}
/* table uses auto-layout so columns size to their content */
table{{min-width:750px;}}
thead th:nth-child(1){{width:44px;}}
/* prevent short-content columns from wrapping; browser expands them to fit */
td:nth-child(1),td:nth-child(3),td:nth-child(4),td:nth-child(7){{white-space:nowrap;}}
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
#pg-top{{position:sticky;top:0;z-index:10;border-top:none;border-bottom:1px solid {T['border']};}}
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
@media(max-width:600px){{
  body{{font-size:12px;}}
  thead th{{padding:8px 8px;font-size:10px;letter-spacing:.4px;}}
  td{{padding:7px 8px;}}
  .badge-hl{{font-size:9px;padding:1px 4px;}}
  .badge-tt{{font-size:10px;padding:2px 6px;}}
  .pg-bar{{padding:8px 10px;gap:4px;}}
  .pg-info{{font-size:11px;}}
  button.pg{{padding:3px 7px;font-size:11px;}}
  .pg-jump{{font-size:11px;}}
  .pg-jump input{{width:38px;}}
}}
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
let sortDir = 1; 
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
  const data = sortedData();
  const total = data.length;
  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;
  if (curPage >= totalPages) curPage = totalPages - 1;
  if (curPage < 0) curPage = 0;

  const start = curPage * PAGE_SIZE;
  const pageData = data.slice(start, start + PAGE_SIZE);

  const tbody = document.getElementById('tbody');
  tbody.innerHTML = pageData.map(r => {{
    return `
      <tr class="${{r.hl ? 'hl' : ''}}">
        <td class="center">${{r.idx}}</td>
        <td><b>${{r.dien_luc}}</b></td>
        <td class="center">${{r.ngay}}</td>
        <td class="center">${{r.tg}}</td>
        <td>${{r.khu_vuc}}${{r.hl ? '<span class="badge-hl">📍 Xuân Trường</span>' : ''}}</td>
        <td>${{r.ly_do}}</td>
        <td class="center"><span class="badge-tt">${{r.tt}}</span></td>
      </tr>
    `;
  }}).join('');

  const pgInfo = `Hiển thị <b>${{total > 0 ? start + 1 : 0}}–${{Math.min(start + PAGE_SIZE, total)}}</b> / ${{total}} lịch`;
  const bars = [document.getElementById('pg-top'), document.getElementById('pg-bot')];
  
  bars.forEach(bar => {{
    bar.innerHTML = `
      <div class="pg-info">${{pgInfo}}</div>
      <div class="pg-btns">
        <button class="pg" ${{curPage === 0 ? 'disabled' : ''}} onclick="changePage(0)">«</button>
        <button class="pg" ${{curPage === 0 ? 'disabled' : ''}} onclick="changePage(${{curPage - 1}})">‹</button>
        ${{renderPageNumbers(totalPages)}}
        <button class="pg" ${{curPage >= totalPages - 1 ? 'disabled' : ''}} onclick="changePage(${{curPage + 1}})">›</button>
        <button class="pg" ${{curPage >= totalPages - 1 ? 'disabled' : ''}} onclick="changePage(${{totalPages - 1}})">»</button>
        <div class="pg-jump">Trang <input type="number" value="${{curPage + 1}}" min="1" max="${{totalPages}}" onchange="changePage(this.value-1)"> / ${{totalPages}}</div>
      </div>
    `;
  }});
}}

function renderPageNumbers(total) {{
  let html = '';
  const range = 2;
  for (let i = 0; i < total; i++) {{
    if (i === 0 || i === total - 1 || (i >= curPage - range && i <= curPage + range)) {{
      html += `<button class="pg ${{i === curPage ? 'active' : ''}}" onclick="changePage(${{i}})">${{i + 1}}</button>`;
    }} else if (i === curPage - range - 1 || i === curPage + range + 1) {{
      html += `<span style="padding:0 4px; opacity:0.5">...</span>`;
    }}
  }}
  return html;
}}

window.changePage = (p) => {{ curPage = p; renderTable(); }};

document.getElementById('thead').onclick = (e) => {{
  const th = e.target.closest('th');
  if (!th) return;
  const col = th.dataset.col;
  if (sortCol === col) sortDir *= -1;
  else {{ sortCol = col; sortDir = 1; }}

  document.querySelectorAll('thead th').forEach(el => el.classList.remove('asc', 'desc'));
  th.classList.add(sortDir === 1 ? 'asc' : 'desc');
  renderTable();
}};

renderTable();
</script>
</body>
</html>
"""

def render_table(df: pd.DataFrame, theme: dict, page_size: int = 20, height: int = 650):
    import streamlit.components.v1 as components
    html = build_table_iframe(df, theme, page_size)
    components.html(html, height=height, scrolling=True)
