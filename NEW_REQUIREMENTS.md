# New Requirements - Scheduler & Telegram Notification

## REQ-001: Scheduled Execution

**Mô tả:** Lập lịch cho app chạy tự động vào các thời điểm cố định hàng ngày.

**Chi tiết:**
- Thời điểm chạy: **12:00 AM (0:00)** và **6:00 AM (6:00)** hàng ngày
- Sử dụng Windows Task Scheduler để đảm bảo chạy ngay cả khi không mở terminal
- Script chạy độc lập, không cần user interaction

---

## REQ-002: Telegram Notification

**Mô tả:** Sau khi lấy dữ liệu, gửi thông báo qua Telegram cho các khu vực được filter.

**Chi tiết:**
- Chỉ gửi thông báo khi có lịch cúp điện ở khu vực được cấu hình trong `HIGHLIGHT_AREAS`
- Nội dung thông báo bao gồm:
  - Điện lực
  - Ngày
  - Thời gian
  - Khu vực
  - Lý do
- Cấu hình Telegram Bot Token và Chat ID qua `.env`

---

## Implementation Plan

### New Files
| File | Description |
|------|-------------|
| `scheduler.py` | Script mới với chức năng lập lịch và gửi Telegram |
| `NEW_REQUIREMENTS.md` | Document này |

### Config Changes (`.env`)
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Windows Task Scheduler Setup
Tạo 2 scheduled tasks chạy `scheduler.py` vào:
- 00:00 hàng ngày
- 06:00 hàng ngày

---

## REQ-003: Streamlit Web UI Dashboard

**Mô tả:** Xây dựng giao diện web trực quan bằng Streamlit để hiển thị lịch cúp điện, hỗ trợ tìm kiếm, lọc dữ liệu và lấy lịch mới nhất từ website.

**Chi tiết:**
- Search bar tổng quát ở trên cùng — lọc realtime theo tất cả các cột
- Button **"Lấy lịch mới nhất"** — gọi lại `core.py` để fetch & parse dữ liệu mới
- **Filter panel:**
  - Multiselect theo **Điện Lực**
  - Text search theo **Khu Vực**
  - Checkbox **"Chỉ hiện khu vực cần theo dõi"** (dựa theo `HIGHLIGHT_AREAS` trong `.env`)
- Bảng dữ liệu định dạng đẹp: `#`, `Điện Lực`, `Ngày`, `Thời gian`, `Khu Vực`, `Lý Do`, `Trạng Thái`
- Các hàng khu vực cần theo dõi được **highlight màu Emerald**
- **Thống kê**: Tổng số lịch, số lịch tại khu vực cần theo dõi
- **Dark / Light mode** toggle — lưu trạng thái trong session
- Auto-load dữ liệu khi mở app lần đầu
- **Màu sắc**: Emerald green (`#10b981`) làm màu chủ đạo
- **Font**: Inter (Google Fonts)

**New Files:**
| File | Description |
|------|-------------|
| `streamlit_app.py` | Streamlit web app chính |
| `requirements_streamlit.txt` | Dependency riêng cho Streamlit app |

**Chạy app:**
```bash
streamlit run streamlit_app.py
```
