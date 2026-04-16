"""
Script hiển thị lịch cúp điện trong console và xuất ra HTML
Chạy thủ công: python lich_cup_dien.py
"""

from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any

# Import từ core module
from core import (
    PROVINCE_NAME,
    POWER_OUTAGE_URL,
    load_table_columns,
    fetch_power_outage_schedule,
    parse_schedule,
    is_highlight_area,
    get_highlight_areas_display,
    export_to_html,
)


def display_schedule(schedules: List[Dict[str, str]], columns: List[Dict[str, Any]]):
    """Hiển thị lịch cúp điện dạng bảng với rich"""
    console = Console()
    
    highlight_areas_display = get_highlight_areas_display()
    
    table = Table(
        title=f"📋 LỊCH CÚP ĐIỆN TỈNH {PROVINCE_NAME.upper()}", 
        title_style="bold magenta",
        show_lines=True,
        header_style="bold white on dark_blue",
        expand=False,
        width=None,
    )
    
    # Thêm các cột từ cấu hình
    for col in columns:
        align = col.get('align', 'left')
        justify_map = {'left': 'left', 'center': 'center', 'right': 'right'}
        justify = justify_map.get(align, 'left')
        
        table.add_column(
            col['label'],
            justify=justify,
            style=col.get('style', 'white'),
            width=col.get('width'),
            max_width=col.get('max_width'),
            no_wrap=col.get('no_wrap', False)
        )
    
    if not schedules:
        console.print("\n[yellow]⚠️  Không có lịch cúp điện nào được tìm thấy.[/yellow]\n")
        return
    
    highlight_count = 0
    
    for idx, schedule in enumerate(schedules, 1):
        khu_vuc = schedule.get('khu_vuc', '')
        
        if is_highlight_area(khu_vuc):
            row_style = "bold orange1"
            highlight_count += 1
        else:
            row_style = None
        
        row_data = []
        for col in columns:
            key = col['key']
            if key == '_index':
                value = str(idx)
            else:
                value = schedule.get(key, '')
            max_len = col.get('max_width') or col.get('width', 50)
            if max_len and len(value) > max_len:
                value = value[:max_len-3] + '...'
            row_data.append(value)
        
        table.add_row(*row_data, style=row_style)
    
    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]📊 Tổng cộng: {len(schedules)} lịch cúp điện[/dim]")
    if highlight_count > 0:
        console.print(f"[bold orange1]🔶 Khu vực {highlight_areas_display}: {highlight_count} lịch cúp điện[/bold orange1]")
    else:
        console.print(f"[dim]🔶 Không có lịch cúp điện tại khu vực {highlight_areas_display}[/dim]")
    console.print()


def main():
    console = Console()
    highlight_areas_display = get_highlight_areas_display()
    
    console.print(f"\n[bold blue]🔌 KIỂM TRA LỊCH CÚP ĐIỆN TỈNH {PROVINCE_NAME.upper()}[/bold blue]")
    console.print(f"[dim]Nguồn: {POWER_OUTAGE_URL}[/dim]")
    console.print(f"[dim]Khu vực cần filter: {highlight_areas_display}[/dim]\n")
    
    columns = load_table_columns()
    
    console.print("[yellow]⏳ Đang tải dữ liệu từ website...[/yellow]")
    html_content = fetch_power_outage_schedule()
    
    if not html_content:
        console.print("[red]❌ Không thể kết nối đến website[/red]")
        return
    
    console.print("[green]✅ Đã tải xong dữ liệu[/green]")
    
    schedules = parse_schedule(html_content)
    display_schedule(schedules, columns)
    
    html_file = export_to_html(schedules, columns)
    if html_file:
        console.print(f"[bold cyan]📄 Đã xuất ra file: {html_file}[/bold cyan]")
        console.print("[dim]Mở file HTML trong trình duyệt để xem đầy đủ hơn.[/dim]\n")


if __name__ == "__main__":
    main()
