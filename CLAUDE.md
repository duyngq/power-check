# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run Streamlit web app (port 8501)
python run.py
# or directly:
streamlit run frontend/app.py

# Run scheduler + Telegram notification (headless)
python backend/scheduler.py

# Run console/HTML output only
python backend/lich_cup_dien.py
```

All commands should be run from the project root. The virtual environment is at `.venv/`.

## Configuration

Copy `.env_example` to `.env`. Key variables:

| Variable | Purpose |
|---|---|
| `POWER_OUTAGE_URL` | Source URL on lichcupdien.org |
| `HIGHLIGHT_AREAS` | Comma-separated areas to highlight/filter (e.g. `Xuân Trường,Tân Mỹ`) |
| `PROVINCE_NAME` | Display name for the province |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_IDS` | Comma-separated Telegram chat IDs for notifications |
| `TABLE_COLUMNS` | JSON array overriding default column config |

## Architecture

The app has a clear backend/frontend split with a single shared core module.

```
backend/core.py          ← All shared logic (scraping, parsing, Telegram, HTML export)
backend/scheduler.py     ← Headless runner: fetch + filter + send Telegram
backend/lich_cup_dien.py ← Console + HTML output (manual use)

frontend/app.py          ← Streamlit entry point; wires sidebar, filters, table
frontend/logic.py        ← Data helpers: fetch_data(), schedules_to_df(), apply_filters()
frontend/styles.py       ← get_theme(is_dark) + apply_custom_css(T) — theme dict drives all CSS
frontend/components/table.py ← Renders data as a self-contained HTML iframe with JS sort + pagination

run.py                   ← Thin launcher: runs `streamlit run frontend/app.py`
```

### Data flow

1. `backend/core.py::fetch_power_outage_schedule()` — HTTP GET to lichcupdien.org
2. `parse_schedule(html)` — BeautifulSoup parses `div.lcd_detail_wrapper` → list of dicts with keys: `dien_luc`, `ngay`, `thoi_gian`, `khu_vuc`, `ly_do`, `trang_thai`
3. `is_highlight_area(khu_vuc)` — substring match against `HIGHLIGHT_AREAS` env var
4. Frontend converts schedules to a pandas DataFrame via `schedules_to_df()`, adding an `_hl` bool column for highlight rows
5. `render_table()` builds a standalone HTML document injected via `st.components.v1.html()` — **not** a native Streamlit dataframe

### Theme system

`frontend/styles.py::get_theme(is_dark)` returns a dict `T` with all color tokens. This dict is threaded through to `apply_custom_css(T)` (Streamlit-level CSS injection) and to `build_table_iframe(df, T)` (iframe HTML). Primary color is Emerald (`#10b981`). Dark/light state lives in `st.session_state.dark_mode`.

### Telegram notifications

`send_telegram_message()` in `core.py` sends in parallel to all `TELEGRAM_CHAT_IDS` using `ThreadPoolExecutor`. Only sends when filtered schedules (matching `HIGHLIGHT_AREAS`) are non-empty.
