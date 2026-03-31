# Hướng dẫn sử dụng API Phishing Detection

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
uvicorn backend:app --host 0.0.0.0 --port 3000
```

Server sẽ chạy tại: `http://localhost:3000`

## API Endpoints

### 1. Health Check
```http
GET /
```
Response:
```json
{"message": "Phishing Detection API", "status": "running"}
```

### 2. Kiểm tra trạng thái
```http
GET /health
```
Response:
```json
{"status": "healthy"}
```

### 3. Predict đơn lẻ
```http
POST /predict
```
Request:
```json
{
  "text": "http://secure-login.bankofamerica.verify-now.tk/account?id=123"
}
```
Response:
```json
{
  "label": "PHISHING",
  "confidence": 0.9734,
  "is_phishing": true
}
```

### 4. Predict nhiều text
```http
POST /predict/batch
```
Request:
```json
[
  "http://secure-login.bankofamerica.verify-now.tk/account?id=123",
  "https://www.google.com/search?q=python+tutorial"
]
```
Response:
```json
[
  {"label": "PHISHING", "confidence": 0.9734, "is_phishing": true},
  {"label": "BENIGN", "confidence": 0.9891, "is_phishing": false}
]
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | "PHISHING" hoặc "BENIGN" |
| `confidence` | float | Độ tin cậy (0-1) |
| `is_phishing` | boolean | True nếu là phishing |

## Ví dụ gọi API từ Frontend

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:3000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'your text here' })
});
const result = await response.json();
console.log(result); // { label: "PHISHING", confidence: 0.97, is_phishing: true }
```

### cURL
```bash
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "http://secure-login.bankofamerica.verify-now.tk/account?id=123"}'
```
