"""
Scheduler script - Chạy tự động lấy lịch cúp điện và gửi thông báo Telegram
Lập lịch chạy lúc 12:00 AM và 6:00 AM hàng ngày
"""

import logging

# Import từ core module
from core import (
    PROVINCE_NAME,
    POWER_OUTAGE_URL,
    TELEGRAM_CHAT_IDS,
    fetch_power_outage_schedule,
    parse_schedule,
    filter_schedules,
    format_telegram_message,
    send_telegram_message,
    get_highlight_areas_display,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_check():
    """Chạy kiểm tra lịch cúp điện và gửi thông báo"""
    logger.info("=" * 50)
    logger.info("Starting power outage check...")
    logger.info(f"URL: {POWER_OUTAGE_URL}")
    logger.info(f"Filter areas: {get_highlight_areas_display()}")
    logger.info(f"Telegram recipients: {len(TELEGRAM_CHAT_IDS)} chat(s)")
    
    # Fetch data
    html_content = fetch_power_outage_schedule()
    if not html_content:
        logger.error("Failed to fetch data")
        return
    
    logger.info("Fetched data successfully")
    
    # Parse data
    schedules = parse_schedule(html_content)
    logger.info(f"Parsed {len(schedules)} schedules")
    
    # Filter for highlight areas
    filtered_schedules = filter_schedules(schedules)
    logger.info(f"Filtered {len(filtered_schedules)} schedules for monitored areas")
    
    # Send Telegram notification if there are matches
    if filtered_schedules:
        message = format_telegram_message(filtered_schedules)
        results = send_telegram_message(message)
        
        # Log results
        if 'error' in results:
            logger.warning(f"Telegram error: {results['error']}")
        else:
            logger.info(f"Telegram send results: {results['success']}/{results['total']} succeeded")
            
            # Log details for each recipient
            for detail in results['details']:
                if detail['success']:
                    logger.info(f"  ✓ Chat {detail['chat_id']}: sent successfully")
                else:
                    logger.warning(f"  ✗ Chat {detail['chat_id']}: failed - {detail['error']}")
    else:
        highlight_areas_display = get_highlight_areas_display()
        logger.info(f"No power outage scheduled for {highlight_areas_display}")
    
    logger.info("Check completed")


def main():
    """Entry point"""
    run_check()


if __name__ == "__main__":
    main()
