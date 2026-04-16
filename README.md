# Lịch Cúp Điện - Power Outage Schedule Scraper

Script Python tự động lấy và hiển thị lịch cúp điện từ [lichcupdien.org](https://lichcupdien.org).

## 1. Features

### Core Features
- ✅ Scrape dữ liệu lịch cúp điện từ website lichcupdien.org
- ✅ Hiển thị dạng table trong console với màu sắc (Rich)
- ✅ Xuất ra file HTML để xem trong trình duyệt
- ✅ Highlight (tô màu cam) các khu vực được cấu hình
- ✅ Cấu hình linh hoạt qua file `.env`

### Scheduler & Notification (v2.0)
- ✅ **Scheduled Execution**: Chạy tự động lúc 00:00 và 06:00 hàng ngày (Windows Task Scheduler)
- ✅ **Telegram Notification**: Gửi thông báo khi có lịch cúp điện ở khu vực được filter
- ✅ **Multi-recipient**: Hỗ trợ gửi đến nhiều Telegram chat IDs
- ✅ **Parallel Sending**: Gửi song song đến tất cả recipients (ThreadPoolExecutor)
- ✅ **Status Tracking**: Log chi tiết trạng thái gửi thành công/thất bại từng recipient

---

## 2. Installation

### Dependencies
```
requests>=2.28.0
beautifulsoup4>=4.11.0
rich>=13.0.0
python-dotenv>=1.0.0
```

### Quick Start
```bash
# Cài đặt dependencies
pip install requests beautifulsoup4 rich python-dotenv

# Chạy manual (hiển thị console + HTML)
python lich_cup_dien.py

# Chạy scheduler (check + gửi Telegram)
python scheduler.py

# Setup scheduled tasks (chạy với Admin)
setup_scheduler.bat
```

---

## 3. Architecture & Code Structure

### Project Structure
```
check_power_off/
├── .env                   # Configuration
├── core.py                # Core module - shared logic
├── template.html          # HTML template
├── lich_cup_dien.py       # Console display (manual)
├── scheduler.py           # Scheduler + Telegram
├── setup_scheduler.bat    # Windows Task Scheduler setup
├── lich_cup_dien.html     # Output (auto-generated)
├── scheduler.log          # Log file (auto-generated)
└── README.md              # Documentation
```

### Module Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                         Entry Points                         │
├─────────────────────────────┬───────────────────────────────┤
│     lich_cup_dien.py        │        scheduler.py           │
│   (Console + HTML output)   │   (Scheduled + Telegram)      │
└─────────────────────────────┴───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         core.py                              │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────┐ │
│  │   Scraper   │ │    Parser    │ │     Telegram API      │ │
│  │ fetch_data  │ │parse_schedule│ │send_telegram_message  │ │
│  └─────────────┘ └──────────────┘ │  (parallel sending)   │ │
│                                   └───────────────────────┘ │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────┐ │
│  │   Filter    │ │ HTML Export  │ │      Config Loader    │ │
│  │is_highlight │ │export_to_html│ │load_table_columns     │ │
│  └─────────────┘ └──────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  .env (Configuration)                        │
│  URL, HIGHLIGHT_AREAS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS │
└─────────────────────────────────────────────────────────────┘
```

### Core Module Functions (`core.py`)

| Function | Description |
|----------|-------------|
| `fetch_power_outage_schedule()` | HTTP GET request đến website |
| `parse_schedule()` | Parse HTML bằng BeautifulSoup |
| `filter_schedules()` | Lọc lịch cúp điện theo khu vực |
| `is_highlight_area()` | Kiểm tra khu vực cần highlight |
| `send_telegram_message()` | Gửi Telegram (parallel, multi-recipient) |
| `format_telegram_message()` | Format message cho Telegram |
| `export_to_html()` | Xuất ra file HTML từ template |
| `load_table_columns()` | Load cấu hình columns từ `.env` |

---

## 4. Configuration (`.env`)

### Basic Config

| Variable | Description | Example |
|----------|-------------|---------|
| `POWER_OUTAGE_URL` | URL lịch cúp điện | `https://lichcupdien.org/lich-cup-dien-lam-dong` |
| `HIGHLIGHT_AREAS` | Khu vực filter (comma-separated) | `Xuân Trường,Tân Mỹ` |
| `PROVINCE_NAME` | Tên tỉnh/thành | `Lâm Đồng` |
| `OUTPUT_HTML_FILE` | File HTML output | `lich_cup_dien.html` |

### Telegram Config

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token từ @BotFather | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_IDS` | Danh sách chat IDs (comma-separated) | `123456789,987654321` |

### Table Columns Config (JSON)
```json
[
  {"key": "_index", "label": "#", "width": 4, "align": "center", "style": "cyan"},
  {"key": "dien_luc", "label": "Điện Lực", "width": 25, "align": "left", "style": "green"},
  {"key": "ngay", "label": "Ngày", "width": 20, "align": "center", "style": "yellow"}
]
```

---

## 5. Telegram Notification

### Setup
1. Chat với [@BotFather](https://t.me/BotFather) để tạo bot mới
2. Lấy `BOT_TOKEN` từ BotFather
3. Chat với [@userinfobot](https://t.me/userinfobot) để lấy `CHAT_ID`
4. Cập nhật `.env`:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF-GHI
TELEGRAM_CHAT_IDS=123456789,987654321,111222333
```

### Multi-recipient Sending
- Gửi **song song** đến tất cả chat IDs bằng `ThreadPoolExecutor`
- Log chi tiết status từng recipient:
```
Telegram send results: 2/3 succeeded
  ✓ Chat 123456789: sent successfully
  ✓ Chat 987654321: sent successfully
  ✗ Chat 111222333: failed - 404 Not Found
```

---

## 6. Scheduled Execution

### Windows Task Scheduler
Chạy `setup_scheduler.bat` với quyền **Administrator** để tạo 2 tasks:
- `PowerOutageCheck_Midnight` - Chạy lúc 00:00 hàng ngày
- `PowerOutageCheck_Morning` - Chạy lúc 06:00 hàng ngày

### Manual Commands
```bash
# Xem tasks
schtasks /query /tn "PowerOutageCheck*"

# Xóa tasks
schtasks /delete /tn "PowerOutageCheck_Midnight" /f
schtasks /delete /tn "PowerOutageCheck_Morning" /f
```

---

## 7. HTML Template

Template sử dụng placeholders `{{...}}`:

| Placeholder | Description |
|-------------|-------------|
| `{{PROVINCE_NAME}}` | Tên tỉnh |
| `{{UPDATE_TIME}}` | Thời gian cập nhật |
| `{{HIGHLIGHT_AREAS}}` | Khu vực được highlight |
| `{{TABLE_HEADERS}}` | Headers của table |
| `{{TABLE_ROWS}}` | Nội dung table rows |
| `{{TOTAL_COUNT}}` | Tổng số lịch |
| `{{HIGHLIGHT_COUNT}}` | Số lịch được highlight |
| `{{SOURCE_URL}}` | URL nguồn |
