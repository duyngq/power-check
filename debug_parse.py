"""
Debug script để xem cấu trúc HTML của trang web
"""

import requests
from bs4 import BeautifulSoup

def fetch_and_debug():
    url = "https://lichcupdien.org/lich-cup-dien-lam-dong"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Lưu HTML ra file để xem
    with open('debug_html.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("HTML đã được lưu vào debug_html.html")
    
    # Tìm các pattern có chứa "Điện lực"
    print("\n=== Tìm các element chứa 'Điện lực' ===")
    for elem in soup.find_all(string=lambda t: t and 'Điện lực' in t):
        parent = elem.find_parent()
        if parent:
            print(f"Tag: {parent.name}, Class: {parent.get('class')}")
            print(f"Text: {elem[:100]}...")
            print("---")

if __name__ == "__main__":
    fetch_and_debug()
