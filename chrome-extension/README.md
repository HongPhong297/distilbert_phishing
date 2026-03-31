# Chrome Extension - Phishing Email Detector

## Cài đặt

### 1. Tạo icons
Tạo thư mục `icons/` và thêm 3 file icon:
- `icon16.png` (16x16)
- `icon48.png` (48x48)  
- `icon128.png` (128x128)

Có thể dùng tool như [Favicon.io](https://favicon.io) để tạo.

### 2. Load Extension vào Chrome

1. Mở Chrome, vào `chrome://extensions/`
2. Bật **Developer mode** (góc phải trên)
3. Click **Load unpacked**
4. Chọn thư mục `chrome-extension/`

### 3. Chạy Backend

```bash
uvicorn backend:app --host 0.0.0.0 --port 3000
```

### 4. Sử dụng

**Cách 1: Scan trực tiếp từ email**
- Mở Gmail/Outlook/Yahoo
- Click vào email cần kiểm tra
- Click icon extension → **Scan Current Email**

**Cách 2: Paste thủ công**
- Click icon extension
- Paste text/URL vào ô
- Click **Analyze**

## Cấu trúc files

```
chrome-extension/
├── manifest.json      # Cấu hình extension
├── popup.html         # Giao diện popup
├── popup.js           # Logic xử lý
├── content.js         # Extract email từ webmail
├── icons/             # Icons (tự tạo)
└── README.md
```

## API Requirements

Backend cần có endpoints:
- `POST /predict` - nhận `{ "text": "..." }`, trả về `{ "label": "PHISHING|BENIGN", "confidence": 0.x, "is_phishing": bool }`
- `GET /health` - health check

## Troubleshooting

### "Cannot connect to API"
- Kiểm tra backend đang chạy `uvicorn backend:app --port 3000`
- Kiểm tra API URL trong Settings popup (mặc định: `http://localhost:3000`)

### Không scan được email
- Đảm bảo đang mở email (không phải inbox)
- Refresh trang email và thử lại

## Tùy chỉnh

Sửa `manifest.json` để thêm domain API thực tế:
```json
"host_permissions": [
  "http://YOUR_API_SERVER:3000/*",
  ...
]
```
