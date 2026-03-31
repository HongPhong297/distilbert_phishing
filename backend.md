# Backend Development Guide

## Mục tiêu
Viết API backend để serve DistilBERT phishing detection model cho Chrome Extension gọi.

---

## 1. Cấu trúc thư mục

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app chính
│   ├── model.py          # Load & inference model
│   ├── schemas.py        # Pydantic models
│   ├── config.py         # Cấu hình
│   └── utils.py          # Helper functions
├── models/               # Lưu model đã convert (ONNX)
├── requirements.txt
├── .env
└── uvicorn_run.py
```

---

## 2. Cài đặt dependencies

```bash
# Core
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
python-dotenv>=1.0.0

# Model optimization (khuyến nghị)
optimum[exporters]>=1.17.0
onnxruntime>=1.17.0

# Hoặc nếu dùng PyTorch trực tiếp
torch>=2.1.0
transformers>=4.40.0
```

---

## 3. Convert Model sang ONNX (Khuyến nghị)

ONNX inference nhanh hơn ~2-3x và không cần PyTorch runtime.

```bash
optimum-cli export onnx \
    --model experiments/distilbert-phishing/best \
    --task text-classification \
    models/onnx/
```

---

## 4. Code mẫu

### 4.1 config.py
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MODEL_PATH: str = "models/onnx"
    API_KEY: str = ""  # Đặt trong .env
    MAX_LENGTH: int = 512
    DEVICE: str = "cpu"  # Hoặc "cuda"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### 4.2 schemas.py
```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    api_key: str | None = None

class PredictResponse(BaseModel):
    label: str  # "BENIGN" hoặc "PHISHING"
    confidence: float  # 0.0 - 1.0
    is_phishing: bool
    processing_time_ms: float
```

### 4.3 model.py
```python
import time
from pathlib import Path
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

class PhishingDetector:
    def __init__(self, model_path: str, max_length: int = 512):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = ORTModelForSequenceClassification.from_pretrained(
            model_path,
            export=True,
        )
        self.max_length = max_length

    def predict(self, text: str) -> dict:
        start = time.perf_counter()

        inputs = self.tokenizer(
            text,
            return_tensors="np",
            truncation=True,
            max_length=self.max_length,
            padding=True,
        )

        outputs = self.model(**inputs)
        logits = outputs.logits[0]

        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()

        phishing_prob = float(probs[1])
        is_phishing = phishing_prob > 0.5
        label = "PHISHING" if is_phishing else "BENIGN"

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "label": label,
            "confidence": phishing_prob if is_phishing else float(probs[0]),
            "is_phishing": is_phishing,
            "processing_time_ms": round(elapsed, 2),
        }

# Singleton
_detector: PhishingDetector | None = None

def get_detector() -> PhishingDetector:
    global _detector
    if _detector is None:
        settings = get_settings()
        _detector = PhishingDetector(settings.MODEL_PATH, settings.MAX_LENGTH)
    return _detector
```

### 4.4 main.py
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.schemas import PredictRequest, PredictResponse
from app.model import get_detector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading model...")
    detector = get_detector()
    logger.info("Model loaded successfully")
    yield

app = FastAPI(
    title="Phishing Detection API",
    description="DistilBERT-based phishing detection for email/URL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Đổi thành domain cụ thể khi deploy
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(api_key: str | None):
    settings = get_settings()
    if settings.API_KEY and api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    api_key: str | None = None,
):
    verify_api_key(api_key)

    detector = get_detector()
    result = detector.predict(request.text)

    return PredictResponse(**result)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 5. API Specification

### POST /predict

**Request:**
```json
{
  "text": "Your PayPal account has been limited. Verify now: http://paypa1.com/verify",
  "api_key": "optional-api-key"
}
```

**Response:**
```json
{
  "label": "PHISHING",
  "confidence": 0.97,
  "is_phishing": true,
  "processing_time_ms": 45.2
}
```

### GET /health
```json
{
  "status": "healthy"
}
```

---

## 6. Deploy

### Local
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models/ ./models/
COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production
- Đặt sau Nginx với HTTPS
- Thêm rate limiting
- API Key authentication bắt buộc
- Cân nhắc cache với Redis cho request trùng lặp

---

## 7. Lưu ý quan trọng

1. **Model path**: Update path trong `.env` trỏ đến thư mục model đã train
2. **ONNX conversion**: Nếu gặp lỗi, có thể dùng PyTorch trực tiếp thay vì ONNX
3. **CORS**: Thay `allow_origins=["*"]` bằng domain cụ thể của extension
4. **API Key**: Tạo key trong `.env` để bảo mật API

---

## Bước tiếp theo

Sau khi có backend chạy, tiếp theo sẽ viết Chrome Extension để gọi API này.
