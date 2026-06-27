# Telegram Message Filter Bot

Bot tu dong loc va forward tin nhan tu nhom Telegram nay sang nhom khac theo keywords.

## Yeu Cau

- Python 3.11+
- Tai khoan Telegram (khong phai bot account)
- API credentials tu https://my.telegram.org/apps

## Cai Dat

```bash
cd telegram-bot-filter
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

## Cau Hinh

Sua file `telegram_config.json`:

```json
{
  "api_id": 123456789,
  "api_hash": "...",
  "phone": "+84xxxxxxxxx",
  "source_chat_id": -100...,
  "target_chat_id": -100...,
  "keywords": ["python", "code"],
  "blocked_users": [],
  "allow_media": false,
  "forward_mode": "copy"
}
```

| Truong | Mo Ta |
|--------|-------|
| `api_id` | Lay tu my.telegram.org/apps |
| `api_hash` | Lay tu my.telegram.org/apps |
| `phone` | So dien thoai Telegram (+84...) |
| `source_chat_id` | Chat ID nhom NGUON |
| `target_chat_id` | Chat ID nhom DICH |
| `keywords` | Danh sach tu khoa (de trong = forward tat ca) |
| `blocked_users` | Danh sach username bi chan |
| `allow_media` | true = cho phep hinh/video, false = chi text |
| `forward_mode` | "copy" (an nguon) hoac "forward" (giu metadata) |

## Lay Chat ID

```bash
python get_chat_ids.py
```

Script se hien thi danh sach tat ca chat kem ID.

## Chay Bot

```bash
python telegram_filter.py
```

Lan dau chay se yeu cau nhap ma xac thuc dien thoai.

## Chay 24/7 tren VPS (Linux)

Tao file `/etc/systemd/system/telegram-filter.service`:

```ini
[Unit]
Description=Telegram Message Filter Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/telegram-bot-filter
ExecStart=/home/telegram-bot-filter/venv/bin/python /home/telegram-bot-filter/telegram_filter.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Sau do:

```bash
systemctl daemon-reload
systemctl enable telegram-filter
systemctl start telegram-filter
systemctl status telegram-filter
```

## Log

- Console: hien thi truc tiep
- File: `filter_log.txt`

## Xu Ly Loi

| Loi | Giai Phap |
|-----|-----------|
| Api key not found | Kiem tra api_id & api_hash |
| Phone not registered | So dien thoai chua co Telegram |
| Chat not found | Chat ID sai hoac chua tham gia nhom |
| ConnectionError | Kiem tra ket noi internet |
