# 📋 PLAN: Telegram Message Filter Bot

---

## 🎯 Mục Đích
Tạo bot tự động copy/forward tin nhắn từ một nhóm Telegram sang nhóm khác, có lọc theo keywords.

---

## 📊 Tổng Quan Project

```
Nhóm Telegram Gốc
      ↓
   Bot Filter (Listen tin mới)
      ↓
  Lọc theo keywords
      ↓
Nhóm Telegram Của Bạn (Nhận tin)
```

---

## 🔧 Tech Stack

| Công Nghệ | Phiên Bản | Mục Đích |
|---|---|---|
| **Python** | 3.11+ | Ngôn ngữ chính |
| **Telethon** | 1.31.1+ | Telegram Client API |
| **JSON** | - | Config file |

---

## 📁 Cấu Trúc Project

```
telegram-bot-filter/
├── telegram_filter.py          # Main bot script
├── telegram_config.json         # Config (keywords, chat IDs)
├── get_chat_ids.py             # Script lấy Chat ID
├── requirements.txt             # Python dependencies
├── session                       # Tạo tự động sau lần chạy đầu
├── README.md                    # Documentation
└── .gitignore                   # Git ignore file
```

---

## ✅ Yêu Cầu Trước Khi Bắt Đầu

### 1. **API Credentials** (từ https://my.telegram.org/apps)
```
- API_ID: (VD: 123456789)
- API_HASH: (VD: "abcdefghijklmnop...")
- PHONE: +84...
```

### 2. **Telegram Chats**
```
- SOURCE_CHAT_ID: Chat ID nhóm gốc
- TARGET_CHAT_ID: Chat ID nhóm của bạn
```

### 3. **Máy Tính**
- Windows / Mac / Linux
- Python 3.11+
- Internet connection

---

## 🚀 Các Bước Implement

### **PHASE 1: LOCAL SETUP (Chạy trên máy Windows)**

#### Bước 1.1: Cài Python
- Download Python 3.11 từ python.org
- Cài với option "Add to PATH"

#### Bước 1.2: Tạo Project Folder
```bash
mkdir telegram-bot-filter
cd telegram-bot-filter
```

#### Bước 1.3: Tạo Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

#### Bước 1.4: Cài Dependencies
```bash
pip install telethon
```

#### Bước 1.5: Tạo File `get_chat_ids.py`
- Script để lấy Chat ID của tất cả nhóm
- Chạy lần đầu để xác định SOURCE_CHAT_ID & TARGET_CHAT_ID

#### Bước 1.6: Tạo File `telegram_config.json`
```json
{
  "api_id": 123456789,
  "api_hash": "...",
  "phone": "+84...",
  "source_chat_id": -100...,
  "target_chat_id": -100...,
  "keywords": ["python", "code"],
  "blocked_users": ["spam_bot"],
  "allow_media": false
}
```

#### Bước 1.7: Tạo File `telegram_filter.py`
- Main bot script
- Các features:
  - Load config từ JSON
  - Đăng nhập Telegram
  - Listen tin nhắn mới từ SOURCE_CHAT_ID
  - Lọc theo keywords
  - Lọc theo blocked_users
  - Lọc theo type (text only / allow media)
  - Forward tin sang TARGET_CHAT_ID
  - Log activity

#### Bước 1.8: Test Local
```bash
python telegram_filter.py
```

---

### **PHASE 2: FEATURES DETAIL**

#### Feature 1: Authentication
- Login qua Telethon
- Tạo session file
- Handle 2FA nếu có

#### Feature 2: Message Listening
- Listen tin mới từ SOURCE_CHAT_ID
- Lấy thông tin: sender, text, timestamp, media

#### Feature 3: Filtering
```
Filter 1: Blocked users (skip nếu từ spam user)
Filter 2: Text only (skip nếu media & allow_media=false)
Filter 3: Keywords (chỉ forward nếu có keyword)
Filter 4: Min text length (optional)
Filter 5: Block links (optional)
```

#### Feature 4: Forwarding
```
Option 1: Forward (giữ metadata gốc)
Option 2: Copy text (giấu gốc)
```

#### Feature 5: Logging
```
- Tin được forward: ✅
- Tin bị skip: ⛔
- Errors: ❌
- Output: Console + File (log.txt)
```

---

### **PHASE 3: VPS DEPLOYMENT (Chạy 24/7)**

#### Bước 3.1: SSH vào VPS VNNIC
```bash
ssh root@IP_VPS
```

#### Bước 3.2: Cài Python trên VPS
```bash
apt update
apt install python3.11 python3.11-venv python3-pip -y
```

#### Bước 3.3: Upload Code lên VPS
```bash
# Dùng SCP hoặc FileZilla
scp -r telegram-bot-filter/ root@IP_VPS:/home/
```

#### Bước 3.4: Setup trên VPS
```bash
cd /home/telegram-bot-filter
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Bước 3.5: Chạy Bot Lần Đầu (Xác Thực)
```bash
python telegram_filter.py
# Nhập phone code khi được hỏi
```

#### Bước 3.6: Setup Systemd Service (Chạy 24/7)
Tạo file `/etc/systemd/system/telegram-filter.service`

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

#### Bước 3.7: Enable & Start Service
```bash
systemctl daemon-reload
systemctl enable telegram-filter
systemctl start telegram-filter

# Check status
systemctl status telegram-filter
```

---

## 📝 Files Cần Tạo

### 1. `telegram_filter.py` (Main Bot)
**Chức năng:**
- Load config
- Login
- Listen events
- Filter messages
- Forward messages
- Log activity

**Code structure:**
```python
from telethon import TelegramClient, events
import json

# Load config
# Khởi tạo client
# Event handler
# Main function
```

### 2. `get_chat_ids.py` (Helper Script)
**Chức năng:**
- Login
- In danh sách tất cả chats
- Giúp user lấy Chat ID

### 3. `telegram_config.json` (Configuration)
```json
{
  "api_id": 123456789,
  "api_hash": "...",
  "phone": "+84...",
  "source_chat_id": -100...,
  "target_chat_id": -100...,
  "keywords": [],
  "blocked_users": [],
  "allow_media": false
}
```

### 4. `requirements.txt`
```
telethon==1.31.1
```

### 5. `README.md` (Documentation)
- Cách setup
- Cách config
- Cách chạy
- Troubleshooting

### 6. `.gitignore`
```
venv/
*.pyc
__pycache__/
session
*.log
.env
```

---

## 🧪 Testing Checklist

- [ ] Bot login thành công
- [ ] Bot nghe tin mới từ SOURCE_CHAT_ID
- [ ] Tin có keyword được forward
- [ ] Tin không có keyword bị skip
- [ ] Tin từ blocked users bị skip
- [ ] Media được xử lý đúng (skip hoặc forward)
- [ ] Log được ghi đúng
- [ ] Bot chạy 24/7 không crash
- [ ] VPS service tự restart khi crash

---

## 📊 Output / Results

### Khi chạy bot:
```
======================================================================
🚀 TELEGRAM MESSAGE FILTER
======================================================================

✅ Đã đăng nhập thành công!

🎯 Bot chạy - sẵn sàng lọc tin nhắn...

======================================================================

✅ FORWARDED
   Từ: Nguyễn Văn A
   Keyword: python, code
   Tin: Có ai biết cách fix bug trong Python không?

⛔ No keywords
   Từ: Trần Văn B
   Tin: Hôm nay thời tiết đẹp

✅ FORWARDED
   Từ: Lê Thị C
   Keyword: api
   Tin: API mới đã up...
```

---

## 🛠️ Configuration Options

### Keywords
```json
"keywords": ["python", "code", "database"]
```
- Chỉ forward tin chứa từ khóa
- Case-insensitive

### Blocked Users
```json
"blocked_users": ["spam_bot", "spammer"]
```
- Skip tin từ những user này

### Allow Media
```json
"allow_media": false
```
- `true`: Forward cả text + hình/video
- `false`: Chỉ forward text

---

## 🚨 Error Handling

| Lỗi | Giải Pháp |
|---|---|
| **Api key not found** | Kiểm tra API_ID & API_HASH |
| **Phone not registered** | Số điện thoại không có Telegram |
| **Timeout** | Chờ xác thực hoặc internet chậm |
| **Chat not found** | Chat ID sai hoặc bot không phải member |
| **Bot account** | Không dùng bot account, dùng user account |

---

## 📈 Future Improvements (Optional)

- [ ] Database (MySQL) để lưu tin
- [ ] Web dashboard để xem logs
- [ ] Multiple source chats (1 bot, nhiều source)
- [ ] Auto restart nếu crash
- [ ] Telegram notification (báo lỗi qua tin nhắn)
- [ ] Blacklist/Whitelist users
- [ ] Time-based filtering (chỉ forward lúc nhất định)
- [ ] Rate limiting

---

## 📞 Support Info

### Cần chuẩn bị:
1. API_ID từ my.telegram.org
2. API_HASH từ my.telegram.org
3. Số điện thoại Telegram
4. Chat ID của 2 nhóm

### Nơi chạy:
- Local: Windows
- Production: VPS VNNIC 50k/tháng

### Support:
- Liên hệ developer nếu có issues
- Check log file để debug

---

## 📅 Timeline

| Phase | Công Việc | Thời Gian |
|---|---|---|
| 1 | Setup local, test features | 30-45 phút |
| 2 | Deploy VPS, config systemd | 30 phút |
| 3 | Testing 24/7 | 1 ngày |
| **Total** | | **~2 giờ** |

---

## ✅ Checklist Hoàn Thành

- [ ] Chuẩn bị API credentials
- [ ] Tạo 2 nhóm Telegram
- [ ] Lấy Chat IDs
- [ ] Code viết xong
- [ ] Test trên Local
- [ ] Deploy lên VPS (optional)
- [ ] Setup systemd service
- [ ] Bot chạy 24/7 ✅

---

**End of Plan**

---

Bây giờ bạn có thể đưa plan này cho **Claude Code** hoặc developer khác để implement! 🚀
