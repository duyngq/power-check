"""
Core module - Chứa logic chung cho việc lấy và xử lý lịch cúp điện
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load cấu hình từ file .env
load_dotenv()

# ===========================================
# Đọc cấu hình từ .env
# ===========================================
POWER_OUTAGE_URL = os.getenv('POWER_OUTAGE_URL', 'https://lichcupdien.org/lich-cup-dien-lam-dong')
HIGHLIGHT_AREAS = [area.strip().lower() for area in os.getenv('HIGHLIGHT_AREAS', 'Xuân Trường').split(',')]
PROVINCE_NAME = os.getenv('PROVINCE_NAME', 'Lâm Đồng')
OUTPUT_HTML_FILE = os.getenv('OUTPUT_HTML_FILE', 'lich_cup_dien.html')

# Telegram config - hỗ trợ nhiều chat ID (phân cách bằng dấu phẩy)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_IDS = [cid.strip() for cid in os.getenv('TELEGRAM_CHAT_IDS', '').split(',') if cid.strip()]

# Đường dẫn đến file template
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'template.html')

# ===========================================
# Cấu hình columns mặc định
# ===========================================
DEFAULT_COLUMNS = [
    {"key": "_index", "label": "#", "width": 4, "align": "center", "style": "cyan"},
    {"key": "dien_luc", "label": "Điện Lực", "width": 25, "align": "left", "style": "green"},
    {"key": "ngay", "label": "Ngày", "width": 20, "align": "center", "style": "yellow"},
    {"key": "thoi_gian", "label": "Thời gian", "width": 15, "align": "center", "style": "blue"},
    {"key": "khu_vuc", "label": "Khu Vực", "width": 40, "align": "left", "style": "white"},
    {"key": "ly_do", "label": "Lý Do", "width": 30, "align": "left", "style": "white"},
    {"key": "trang_thai", "label": "Trạng Thái", "width": 12, "align": "center", "style": "green"},
]

# Mapping từ tên field website sang key
FIELD_MAPPING = {
    'Điện lực': 'dien_luc',
    'Ngày': 'ngay',
    'Thời gian': 'thoi_gian',
    'Khu vực': 'khu_vuc',
    'Lý do': 'ly_do',
    'Trạng thái': 'trang_thai',
}

# Giá trị mặc định cho các field
FIELD_DEFAULTS = {
    'dien_luc': '',
    'ngay': '',
    'thoi_gian': '',
    'khu_vuc': '',
    'ly_do': 'Bảo trì định kỳ',
    'trang_thai': 'Đã duyệt',
}


def load_table_columns() -> List[Dict[str, Any]]:
    """Load cấu hình columns từ .env hoặc dùng mặc định"""
    columns_json = os.getenv('TABLE_COLUMNS')
    if columns_json:
        try:
            return json.loads(columns_json)
        except json.JSONDecodeError:
            print("⚠️ Lỗi parse TABLE_COLUMNS, sử dụng cấu hình mặc định")
    return DEFAULT_COLUMNS


def fetch_power_outage_schedule() -> Optional[str]:
    """Lấy dữ liệu lịch cúp điện từ website"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(POWER_OUTAGE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        print(f"Lỗi khi truy cập website: {e}")
        return None


def parse_schedule(html_content: str) -> List[Dict[str, str]]:
    """Parse HTML để lấy thông tin lịch cúp điện"""
    soup = BeautifulSoup(html_content, 'html.parser')
    schedules = []
    
    detail_wrappers = soup.find_all('div', class_='lcd_detail_wrapper')
    
    for wrapper in detail_wrappers:
        schedule = {}
        rows = wrapper.find_all('div', class_='new_lcd_wrapper')
        
        for row in rows:
            title_elem = row.find('span', class_='title_item_lcd_wrapper')
            content_elem = row.find('span', class_='content_item_content_lcd_wrapper')
            
            if title_elem and content_elem:
                title = title_elem.get_text(strip=True).replace(':', '')
                content = content_elem.get_text(strip=True)
                
                for field_name, field_key in FIELD_MAPPING.items():
                    if field_name in title:
                        schedule[field_key] = content
                        break
        
        if schedule.get('dien_luc') and schedule.get('ngay'):
            for key, default_value in FIELD_DEFAULTS.items():
                schedule.setdefault(key, default_value)
            schedules.append(schedule)
    
    return schedules


def is_highlight_area(khu_vuc: str) -> bool:
    """Kiểm tra xem khu vực có cần highlight không"""
    khu_vuc_lower = khu_vuc.lower()
    return any(area in khu_vuc_lower for area in HIGHLIGHT_AREAS)


def filter_schedules(schedules: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Lọc ra các lịch cúp điện ở khu vực cần theo dõi"""
    return [s for s in schedules if is_highlight_area(s.get('khu_vuc', ''))]


def get_highlight_areas_display() -> str:
    """Lấy danh sách khu vực highlight dạng hiển thị"""
    return ', '.join([a.title() for a in HIGHLIGHT_AREAS])


def send_telegram_to_chat(chat_id: str, message: str) -> Tuple[str, bool, str]:
    """Gửi message đến 1 chat ID cụ thể
    Returns: (chat_id, success, error_message)
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return (chat_id, True, '')
    except requests.RequestException as e:
        return (chat_id, False, str(e))


def send_telegram_message(message: str) -> Dict[str, Any]:
    """Gửi message qua Telegram Bot đến tất cả chat IDs (song song)
    Returns: Dict với thông tin status của từng chat
    """
    results = {
        'total': len(TELEGRAM_CHAT_IDS),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    if not TELEGRAM_BOT_TOKEN:
        results['error'] = 'TELEGRAM_BOT_TOKEN not configured'
        return results
    
    if not TELEGRAM_CHAT_IDS:
        results['error'] = 'TELEGRAM_CHAT_IDS not configured'
        return results
    
    if not message:
        results['error'] = 'Empty message'
        return results
    
    # Gửi song song đến tất cả chat IDs
    with ThreadPoolExecutor(max_workers=min(10, len(TELEGRAM_CHAT_IDS))) as executor:
        futures = {
            executor.submit(send_telegram_to_chat, chat_id, message): chat_id 
            for chat_id in TELEGRAM_CHAT_IDS
        }
        
        for future in as_completed(futures):
            chat_id, success, error = future.result()
            detail = {
                'chat_id': chat_id,
                'success': success,
                'error': error if not success else None
            }
            results['details'].append(detail)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
    
    return results


def format_telegram_message(schedules: List[Dict[str, str]]) -> str:
    """Format message để gửi Telegram"""
    if not schedules:
        return ""
    
    highlight_areas_display = get_highlight_areas_display()
    
    message = f"🔌 *LỊCH CÚP ĐIỆN {PROVINCE_NAME.upper()}*\n"
    message += f"📍 Khu vực: {highlight_areas_display}\n"
    message += f"🕐 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    message += "━" * 30 + "\n\n"
    
    for idx, schedule in enumerate(schedules, 1):
        message += f"*{idx}. {schedule.get('dien_luc', 'N/A')}*\n"
        message += f"   📅 Ngày: {schedule.get('ngay', 'N/A')}\n"
        message += f"   ⏰ Thời gian: {schedule.get('thoi_gian', 'N/A')}\n"
        message += f"   📍 Khu vực: {schedule.get('khu_vuc', 'N/A')}\n"
        message += f"   📝 Lý do: {schedule.get('ly_do', 'N/A')}\n"
        message += "\n"
    
    message += "━" * 30 + "\n"
    message += f"📊 Tổng: {len(schedules)} lịch cúp điện"
    
    return message


def export_to_html(schedules: List[Dict[str, str]], columns: List[Dict[str, Any]]) -> Optional[str]:
    """Xuất kết quả ra file HTML sử dụng template"""
    
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file template: {TEMPLATE_FILE}")
        return None
    
    header_columns = ""
    for col in columns:
        header_columns += f"                <th>{col['label']}</th>\n"
    
    table_rows = ""
    highlight_count = 0
    highlight_areas_display = get_highlight_areas_display()
    
    for idx, schedule in enumerate(schedules, 1):
        khu_vuc = schedule.get('khu_vuc', '')
        is_highlighted = is_highlight_area(khu_vuc)
        if is_highlighted:
            highlight_count += 1
        
        row_class = 'highlight' if is_highlighted else ''
        
        row_cells = ""
        for col in columns:
            key = col['key']
            if key == '_index':
                value = str(idx)
            else:
                value = schedule.get(key, '')
            row_cells += f"                <td>{value}</td>\n"
        
        table_rows += f"""            <tr class="{row_class}">
                {row_cells}            </tr>
"""
    
    html_content = template.replace('{{PROVINCE_NAME}}', PROVINCE_NAME)
    html_content = html_content.replace('{{PROVINCE_NAME_UPPER}}', PROVINCE_NAME.upper())
    html_content = html_content.replace('{{UPDATE_TIME}}', datetime.now().strftime("%d/%m/%Y %H:%M"))
    html_content = html_content.replace('{{HIGHLIGHT_AREAS}}', highlight_areas_display)
    html_content = html_content.replace('{{TABLE_HEADERS}}', header_columns)
    html_content = html_content.replace('{{TABLE_ROWS}}', table_rows)
    html_content = html_content.replace('{{TOTAL_COUNT}}', str(len(schedules)))
    html_content = html_content.replace('{{HIGHLIGHT_COUNT}}', str(highlight_count))
    html_content = html_content.replace('{{SOURCE_URL}}', POWER_OUTAGE_URL)
    
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_HTML_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path
