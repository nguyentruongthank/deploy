# du_doan_de_telegram.py

import requests
from bs4 import BeautifulSoup
from collections import Counter
import datetime
import time
import os


def get_gdb_result(date_str):
    """
    Lấy 2 số cuối của giải đặc biệt từ Minh Ngọc theo định dạng dd-mm-yyyy
    """
    url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{date_str}.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        gdb_cell = soup.find('table', class_='bkqmienbac').find_all('td')[1]
        gdb = gdb_cell.text.strip()
        return gdb[-2:] if len(gdb) >= 2 else None
    except Exception as e:
        print(f"Lỗi lấy dữ liệu {date_str}: {e}")
        return None


def collect_de_history(start_year=2000, end_date=None):
    if end_date is None:
        end_date = datetime.date.today()
    start_date = datetime.date(start_year, 1, 1)
    de_list = []
    current_date = start_date

    print(f"📊 Bắt đầu thu thập từ {start_date} đến {end_date}...")
    while current_date <= end_date:
        date_str = current_date.strftime("%d-%m-%Y")
        de = get_gdb_result(date_str)
        if de:
            de_list.append(de)
        current_date += datetime.timedelta(days=1)
        time.sleep(0.3)  # để tránh bị chặn
    print(f"✅ Hoàn tất thu thập: {len(de_list)} kết quả.")
    return de_list


def suggest_top_10_so_de(de_history):
    counter = Counter(de_history)
    top_10 = counter.most_common(10)
    print("🔮 Top 10 số đề nhiều nhất:")
    for so, count in top_10:
        print(f"  → {so}: {count} lần")
    return top_10


def send_to_telegram(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("📨 Đã gửi kết quả tới Telegram.")
        else:
            print(f"❌ Gửi Telegram thất bại: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi Telegram: {e}")


if __name__ == "__main__":
    # Đọc biến môi trường từ Render
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Thiếu biến môi trường TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
        exit(1)

    today = datetime.date.today()
    de_history = collect_de_history(start_year=2000, end_date=today)
    top_10 = suggest_top_10_so_de(de_history)

    # Soạn tin nhắn
    message = f"*📅 Dự đoán 10 số đề ngày {today.strftime('%d/%m/%Y')}*\n\n"
    for so, count in top_10:
        message += f"• `{so}` — {count} lần\n"
    message += "\n🎯 Chúc bạn may mắn hôm nay!"

    send_to_telegram(message, BOT_TOKEN, CHAT_ID)
