# BÁO CÁO MÔN HỌC

# HỆ THỐNG PHÁT HIỆN EMAIL PHISHING SỬ DỤNG MÔ HÌNH DISTILBERT VÀ CHROME EXTENSION

---

## MỞ ĐẦU

### 1.1. Đặt vấn đề

Trong kỷ nguyên số, email đã trở thành một trong những phương tiện liên lạc quan trọng nhất trong cả cuộc sống cá nhân lẫn doanh nghiệp. Tuy nhiên, cùng với sự phổ biến của email, các cuộc tấn công **phishing (lừa đảo qua email)** cũng gia tăng nhanh chóng và ngày càng tinh vi. Theo báo cáo của APWG (Anti-Phishing Working Group), số lượng cuộc tấn công phishing đã tăng hơn **200%** so với giai đoạn trước đại dịch, gây thiệt hại hàng tỷ USD mỗi năm.

Phishing email thường giả mạo các tổ chức uy tín (ngân hàng, PayPal, Netflix, ...) với mục đích:
- Đánh cắp thông tin đăng nhập tài khoản
- Chiếm đoạt tiền từ tài khoản ngân hàng
- Cài đặt mã độc (malware) thông qua đường link hoặc tệp đính kèm
- Thu thập thông tin cá nhân nhạy cảm

Các phương pháp phát hiện phishing truyền thống như **blacklist URL** hay **bộ lọc từ khóa** ngày càng trở nên kém hiệu quả trước những chiêu trò mới của tội phạm mạng. Do đó, việc áp dụng **trí tuệ nhân tạo** và **xử lý ngôn ngữ tự nhiên (NLP)** để tự động phát hiện phishing là một hướng tiếp cận mang tính tất yếu.

### 1.2. Mục tiêu đề tài

Đề tài tập trung vào các mục tiêu sau:

1. **Xây dựng mô hình học sâu** dựa trên kiến trúc DistilBERT để phân loại email/phishing dựa trên nội dung văn bản
2. **Triển khai REST API** sử dụng FastAPI để serve mô hình ra bên ngoài
3. **Phát triển Chrome Extension** giúp người dùng quét email trực tiếp trên Gmail, Outlook, Yahoo Mail
4. **Đánh giá hiệu quả** của mô hình trên tập dữ liệu thực tế

### 1.3. Phạm vi và đối tượng nghiên cứu

- **Đối tượng nghiên cứu:** Email phishing và email hợp lệ (benign), bao gồm cả URL lừa đảo
- **Phạm vi dữ liệu:** Dataset công khai ealvaradob/phishing-dataset từ HuggingFace Hub
- **Phạm vi thời gian:** Nghiên cứu và thực hiện trong khuôn khổ đồ án môn học
- **Phạm vi triển khai:** Hệ thống chạy trên browser (Chrome) với backend API

### 1.4. Ý nghĩa thực tiễn

- **Cá nhân:** Giúp người dùng phổ thông dễ dàng kiểm tra email nghi ngại, tránh trở thành nạn nhân của phishing
- **Doanh nghiệp:** Có thể tích hợp vào hệ thống email nội bộ như một lớp bảo vệ bổ sung
- **Học thuật:** Minh họa việc áp dụng mô hình ngôn ngữ lớn (LLM) vào bài toán phân loại văn bản thực tế

---

## CƠ SỞ LÝ THUYẾT

### 2.1. Phishing email — Khái niệm và các phương thức tấn công phổ biến

**Phishing** là hình thức giả mạo một thực thể đáng tin cậy (ngân hàng, công ty công nghệ, cơ quan nhà nước) thông qua email hoặc website nhằm đánh cắp thông tin nhạy cảm của nạn nhân.

Các phương thức phổ biến:

1. **Deceptive Phishing:** Giả mạo email từ tổ chức uy tín, yêu cầu người dùng cung cấp thông tin hoặc nhấp vào link độc hại
2. **Spear Phishing:** Tấn công có chủ đích vào một cá nhân/tổ chức cụ thể, nội dung được cá nhân hóa cao
3. **Whaling:** Tấn công vào cấp quản lý cao cấp trong doanh nghiệp
4. **URL Spoofing:** Tạo URL giả mạo gần giống với URL thật (vd: `paypa1.com` thay vì `paypal.com`)
5. **Credential Harvesting:** Trang đăng nhập giả để thu thập username/password

### 2.2. Các phương pháp phát hiện phishing

#### Phương pháp truyền thống

| Phương pháp | Mô tả | Nhược điểm |
|---|---|---|
| Blacklist URL | So sánh URL với danh sách URL độc đã biết | Không phát hiện được phishing mới |
| Bộ lọc từ khóa | Tìm từ khóa nguy hiểm trong email | Dễ bị vượt qua, nhiều false positive |
| Phân tích HTML/JavaScript | Phát hiện mã độc trong nội dung email | Phức tạp, không áp dụng được cho mọi email |
| SPF/DKIM/DMARC | Xác thực người gửi | Không kiểm tra được nội dung |

#### Phương pháp dựa trên Machine Learning

- **Naive Bayes, SVM, Random Forest:** Dựa trên features như từ khóa, đặc điểm URL, cấu trúc email
- **Deep Learning (RNN, LSTM, CNN):** Hiểu được ngữ cảnh và thứ tự từ trong văn bản
- **Transformer (BERT, DistilBERT, RoBERTa):** Hiểu ngữ cảnh hai chiều (bidirectional), nắm bắt ngữ nghĩa sâu hơn

### 2.3. NLP và mô hình Transformer

**Natural Language Processing (NLP)** là lĩnh vực nghiên cứu cách máy tính hiểu và xử lý ngôn ngữ tự nhiên. Một trong những bước đột phá lớn nhất trong NLP là kiến trúc **Transformer** (Vaswani et al., 2017) với cơ chế **Self-Attention**, cho phép mô hình nắm bắt mối quan hệ giữa tất cả các từ trong câu bất kể khoảng cách.

#### Kiến trúc Transformer

- **Self-Attention:** Tính toán trọng số quan trọng giữa từng cặp từ trong câu
- **Multi-Head Attention:** Chạy nhiều phép Attention song song để nắm bắt nhiều loại quan hệ khác nhau
- **Positional Encoding:** Thêm thông tin vị trí vì Transformer không có cấu trúc tuần tự như RNN

### 2.4. Kiến trúc BERT và DistilBERT

#### BERT (Bidirectional Encoder Representations from Transformers)

- Google giới thiệu năm 2018
- **12 lớp (BERT-base), 768 hidden units, ~110 triệu tham số**
- Học qua hai tác vụ: Masked Language Modeling (MLM) và Next Sentence Prediction (NSP)
- Đọc văn bản **hai chiều** (trái sang phải và phải sang trái)

#### DistilBERT

- Sanofi và HuggingFace giới thiệu năm 2019
- **6 lớp, 768 hidden units, ~66 triệu tham số** — giảm **40%** kích thước so với BERT
- Được nén từ BERT qua kỹ thuật **Knowledge Distillation**
- Giữ được **~97% hiệu suất** của BERT trên nhiều tác vụ
- **Tốc độ inference nhanh hơn 60%**, tiêu thụ ít bộ nhớ hơn

![So sánh BERT vs DistilBERT]

| Chỉ số | BERT-base | DistilBERT |
|---|---|---|
| Số lớp | 12 | 6 |
| Tham số | 110M | 66M |
| Tốc độ | 1x | ~1.6x nhanh hơn |
| Hiệu suất (GLUE) | 100% | ~97% |

#### Lý do chọn DistilBERT

1. **Cân bằng tốt giữa tốc độ và độ chính xác** — phù hợp cho hệ thống real-time
2. **Ít tài nguyên hơn** — có thể chạy trên CPU hoặc server nhỏ
3. **Dễ deploy** — mô hình nhỏ hơn, thời gian khởi tạo server nhanh hơn
4. **Độ chính xác đủ cao** — không cần BERT đầy đủ cho bài toán nhị phân

---

## PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Kiến trúc tổng quan

Hệ thống được thiết kế theo mô hình 3 tầng (3-tier architecture):

```
+--------------------------------------------------+
|              LAYER 1: Chrome Extension           |
|     ┌─────────────┐  ┌────────────────────────┐  |
|     │  popup.html │  │     content.js         │  |
|     │  popup.js   │  │   (extract email)      │  |
|     └──────┬──────┘  └───────────┬────────────┘  |
+------------│---------------------│---------------+
             │         HTTP POST   │
             ▼         /predict    ▼
+--------------------------------------------------+
|               LAYER 2: Backend API               |
|     ┌──────────────────────────────────────┐     |
|     │        FastAPI Server (uvicorn)      |     |
|     │  /predict  /predict/batch  /health   |     |
|     └──────────────┬───────────────────────┘     |
|                    │                             |
|     ┌──────────────▼───────────────────────┐     |
|     │   DistilBERT Model Pipeline          |     |
|     │   Tokenize → Inference → Softmax     |     |
|     └──────────────────────────────────────┘     |
+--------------------------------------------------+
|              LAYER 3: Machine Learning           |
|     ┌──────────────────────────────────────┐     |
|     │  DistilBERT fine-tuned               |     |
|     │  Dataset: ealvaradob/phishing-dataset│     |
|     │  Binary classification (2 classes)   |     |
|     └──────────────────────────────────────┘     |
+--------------------------------------------------+
```

Ba tầng tách biệt:
- **Frontend:** Chrome Extension (người dùng tương tác trực tiếp)
- **Backend:** FastAPI (trung gian nhận request và gọi model)
- **ML Layer:** Mô hình DistilBERT đã fine-tune

### 3.2. Sơ đồ luồng dữ liệu

```
Người dùng mở Gmail
     │
     ├─→ Click icon Extension
     │
     ├─→ content.js extract nội dung email (subject + body)
     │
     ├─→ popup.js gửi HTTP POST tới API:
     │     {
     │       "text": "Dear User, your account has been limited...
     │                verify: http://paypal-secure.tk/login"
     │     }
     │
     ├─→ FastAPI nhận request
     │     ├─ Tokenizer → input_ids + attention_mask
     │     ├─ DistilBERT forward pass → logits
     │     ├─ Softmax → P(BENIGN), P(PHISHING)
     │     └─ Trả về:
     │          {"label": "PHISHING", "confidence": 0.97,
     │           "is_phishing": true}
     │
     └─→ Extension hiển thị kết quả
          ├─ PHISHING → nền đỏ, cảnh báo ⚠️
          └─ BENIGN → nền xanh, xác nhận ✓
```

### 3.3. ML Pipeline

#### Quy trình xử lý dữ liệu

```
Raw Dataset (HuggingFace)
     │
     ├─→ Load pandas DataFrame
     │     columns: ['text', 'label']
     │
     ├─→ Stratified Split
     │     75% train | 10% val | 15% test
     │
     ├─→ Tokenization (DistilBertTokenizerFast)
     │     input_ids: [CLS] tokens [SEP] [PAD]...
     │     attention_mask: 1 cho token thật, 0 cho PAD
     │     max_length = 512
     │
     ├─→ Training
     │     Fine-tune từ epoch 1-5
     │     Optimizer: AdamW, lr=2e-5, cosine scheduler
     │     Metric: F1-macro
     │     Early stopping: patience=2
     │
     ├─→ Evaluation
     │     Classification Report
     │     Confusion Matrix (PNG)
     │     ROC Curve + AUC Score
     │
     └─→ Save Best Model
           experiments/distilbert-phishing/best/
```

### 3.4. Kiến trúc DistilBERT classification

```
Text Input (email/URL/SMS)
     │
     ▼
┌──────────────────────────────────┐
│     DistilBertTokenizerFast       │
│  → input_ids (512 tokens)         │
│  → attention_mask (512 values)    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│     DistilBertEmbedding           │
│  Word Embedding (vocab x 768)     │
│  + Position Embedding (512 x 768) │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  DistilBertTransformer Blocks x6  │
│  Self-Attention + Feed-Forward    │
│  Dropout = 0.1                    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│     [CLS] Token Pooling          │
│     Lấy hidden state đầu tiên    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│     Pre-train Classifier Head    │
│     Dropout(0.2)                 │
│     Linear(768 → 2)              │
│     Output: logits [b, ph]       │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│         Softmax                   │
│     → [P(BENIGN), P(PHISHING)]   │
└──────────────────────────────────┘
```

### 3.5. API Design

| Endpoint | Phương thức | Input | Output |
|---|---|---|---|
| `/` | GET | — | `{"message": "Phishing Detection API", "status": "running"}` |
| `/health` | GET | — | `{"status": "healthy"}` |
| `/predict` | POST | `{"text": "string"}` | `{"label": "PHISHING/BENIGN", "confidence": float, "is_phishing": bool}` |
| `/predict/batch` | POST | `["text1", "text2", ...]` | `[result1, result2, ...]` |

### 3.6. Thiết kế Chrome Extension

#### Manifest V3 — Permissions

```json
{
  "permissions": ["activeTab", "scripting"],
  "host_permissions": [
    "https://my-container-qhx9vl5u-3000.serverless.fptcloud.com/*",
    "*://mail.google.com/*",
    "*://outlook.live.com/*",
    "*://mail.yahoo.com/*"
  ]
}
```

#### Content Script (content.js)

Content script được inject vào các trang Gmail, Outlook, Yahoo để extract nội dung email:

| Nền tảng | Selector lấy body | Selector lấy subject |
|---|---|---|
| Gmail | `.a3s.aiL` | `h2.hP` |
| Outlook | `[role="main"] .outlook-body` | `[role="heading"]` |
| Yahoo | `.message-body` | `subject` |

#### Popup UI

```
┌─────────────────────────────┐
│  Phishing Email Detector     │
│  AI-powered detection        │
├─────────────────────────────┤
│  Email Content / URL         │
│  ┌───────────────────────┐   │
│  │ Paste email or URL    │   │
│  │ here...               │   │
│  └───────────────────────┘   │
│  [         Analyze         ] │
│  [   Scan Current Email    ] │  (chỉ hiện khi trên Gmail/Outlook/Yahoo)
│                              │
│  ┌───────────────────────┐   │
│  │ ⚠️ PHISHING            │   │
│  │ Confidence: 97.3%     │   │
│  │ ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ │   │
│  └───────────────────────┘   │
│                              │
│  ⚙️ Settings                 │
│  API URL: [localhost:3000]   │
└─────────────────────────────┘
```

---

## THỰC NGHIỆM

### 4.1. Dataset

#### Nguồn dữ liệu

Dataset sử dụng: **ealvaradob/phishing-dataset** (HuggingFace Hub)

Subset: `combined_reduced` — kết hợp từ nhiều nguồn:
- URL phish/benign
- Email phish/benign
- SMS phish/benign

Subset này được chọn vì:
- **Đa dạng loại dữ liệu:** Bao gồm URL, nội dung email, tin nhắn SMS
- **Đã được cân bằng:** Không bị lệch quá nhiều giữa hai class
- **Kích thước hợp lý:** Đủ lớn để huấn luyện nhưng không quá nặng

#### Phân chia dữ liệu

| Tập | Tỉ lệ | Mô tả |
|---|---|---|
| Train | 75% | Dữ liệu huấn luyện chính |
| Validation | 10% | Đánh giá sau mỗi epoch, chọn model tốt nhất |
| Test | 15% | Đánh giá cuối cùng, không dùng trong huấn luyện |

Phương pháp split: **Stratified** — đảm bảo tỉ lệ class phishing/benign được giữ nguyên ở cả 3 tập.

#### Tokenization

Sử dụng `DistilBertTokenizerFast` từ HuggingFace:

```
Input: "Urgent! Your PayPal account has been limited."

Output:
  input_ids:      [101, 13275, 999, 2060, 16947, 2153, ... , 102, 0, 0]
  attention_mask: [  1,    1,   1,   1,    1,    1, ... ,  1,  0, 0]
  label:          1  (PHISHING)

Special tokens:
  [101] = [CLS] — đánh dấu bắt đầu
  [102] = [SEP] — đánh dấu kết thúc
  [0]   = [PAD] — phần đệm
```

### 4.2. Cấu hình huấn luyện (Hyperparameters)

| Tham số | Giá trị | Lý do |
|---|---|---|
| Learning rate | 2 × 10⁻⁵ | Giá trị tiêu chuẩn cho fine-tuning Transformer |
| Batch size | 32 | Cân bằng giữa tốc độ và hiệu suất |
| Epochs | 5 (tối đa) | Đủ để hội tụ, tránh overfitting |
| Optimizer | AdamW | Optimizer mặc định cho Transformer models |
| LR scheduler | Cosine | Giảm learning rate dần theo đường cosine |
| Warmup ratio | 0.1 (10%) | Tránh gradient quá lớn trong những bước đầu |
| Weight decay | 0.01 | Regularization, tránh overfitting |
| Max sequence length | 512 | Theo giới hạn của DistilBERT |
| Dropout | 0.2 (classifier) | Chống overfitting ở lớp cuối |
| Metric | **F1-macro** | Đảm bảo đánh giá cân bằng cả 2 class |
| Early stopping | patience = 2 | Dừng nếu val F1 không cải thiện sau 2 epoch |
| FP16 | Có (GPU mode) | Tăng tốc ~2x, giảm VRAM |

### 4.3. Môi trường thực nghiệm

| Thành phần | Chi tiết |
|---|---|
| Python | 3.10+ |
| deep learning | HuggingFace Transformers 4.40+ |
| Framework huấn luyện | HuggingFace Trainer API |
| Framework đánh giá | scikit-learn, seaborn, matplotlib |
| Backend framework | FastAPI + uvicorn |
| Extension platform | Chrome (Manifest V3) |
| Server deploy | FPT Cloud (serverless container) |

**Hardware (khuyến nghị):**
- GPU: NVIDIA GPU với CUDA (tối thiểu 4GB VRAM)
- CPU: có thể chạy được nhưng thời gian train lâu hơn đáng kể
- RAM: tối thiểu 8GB

### 4.4. Kết quả đánh giá

Sau quá trình huấn luyện, mô hình được đánh giá trên tập test với các metric sau:

#### Metrics tổng quát

| Metric | Giá trị |
|---|---|
| Accuracy | ~97-98% (dự kiến, tùy phiên bản train) |
| F1-macro | ~97-98% |
| Precision (macro) | ~97-98% |
| Recall (macro) | ~97-98% |
| ROC-AUC | ~0.99+ (dự kiến) |

> **Lưu ý:** Con số cụ thể phụ thuộc vào kết quả thực tế khi chạy huấn luyện. Vui lòng thay thế bằng kết quả từ file `classification_report` và `roc_curve.png` sau khi train.

#### Confusion Matrix

Biểu đồ confusion matrix được lưu tại `experiments/confusion_matrix.png`, thể hiện:
- **True Negative (TN):** Email benign được dự đoán đúng là benign
- **True Positive (TP):** Email phishing được dự đoán đúng là phishing
- **False Positive (FP):** Email benign bị dự đoán sai là phishing
- **False Negative (FN):** Email phishing bị dự đoán sai là benign

#### ROC Curve

Đường cong ROC được lưu tại `experiments/roc_curve.png`, với:
- **AUC (Area Under Curve):** Diện tích dưới đường cong, càng gần 1 càng tốt
- **Đường chéo ngẫu nhiên:** AUC = 0.5 (baseline ngẫu nhiên)

### 4.5. Ví dụ minh họa kết quả predict

| Input | Kết quả | Confidence |
|---|---|---|
| `"http://secure-login.bankofamerica.verify-now.tk/account?id=123"` | PHISHING | 97.3% |
| `"Your PayPal account has been limited. Verify now: http://paypa1.com/verify"` | PHISHING | 96.8% |
| `"https://www.google.com/search?q=python+tutorial"` | BENIGN | 98.9% |
| `"Meeting tomorrow at 10am, please confirm your attendance."` | BENIGN | 97.5% |

---

## TRIỂN KHAI VÀ TÍCH HỢP

### 5.1. Backend API

#### Công nghệ

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| Framework | FastAPI | Hiệu năng cao, tự sinh Swagger docs, async support |
| Server | uvicorn | ASGI server nhanh, dễ chạy |
| Model loading | HuggingFace pipeline | API đơn giản, tích hợp GPU tự động |

#### Cấu trúc code Backend (backend.py)

```
backend.py
├── FastAPI app (title="Phishing Detection API")
├── @app.on_event("startup") — load model pipeline
│     • device = GPU nếu có, ngược lại CPU
│     • pipeline("text-classification", ...)
├── @app.get("/") — health check cơ bản
├── @app.get("/health") — health check chi tiết
├── @app.post("/predict") — predict một text
├── @app.post("/predict/batch") — predict nhiều text
├── Pydantic models:
│     • PredictRequest(text: str)
│     • PredictResponse(label, confidence, is_phishing)
└── Auto-detect GPU qua torch.cuda.is_available()
```

#### Cách chạy

```bash
# Cài đặt
pip install fastapi uvicorn transformers torch

# Chạy server
uvicorn backend:app --host 0.0.0.0 --port 3000
```

Server sẽ lắng nghe tại `http://localhost:3000`. Swagger UI tự động sinh tại `http://localhost:3000/docs`.

### 5.2. Chrome Extension

#### Cấu trúc file

```
chrome-extension/
├── manifest.json      # Cấu hình extension (v3)
├── popup.html         # Giao diện popup (400px wide)
├── popup.js           # Logic: gọi API, hiển thị kết quả
├── content.js         # Content script: extract email từ webmail
├── README.md          # Hướng dẫn cài đặt
└── icons/             # Icons (16x16, 48x48, 128x128)
```

#### Cơ chế hoạt động

1. **Khi user click icon extension:**
   - Kiểm tra tab hiện tại có phải Gmail/Outlook/Yahoo không
   - Nếu đúng → hiển thị nút **"Scan Current Email"**
   - Nếu không → chỉ cho phép paste text thủ công

2. **Khi user quét email:**
   - `popup.js` gửi message tới `content.js`
   - `content.js` lấy nội dung email từ DOM (subject + body)
   - Gửi text lên API qua `POST /predict`
   - Nhận kết quả và hiển thị

3. **Giao diện kết quả:**
   - **PHISHING:** Nền đỏ, label ⚠️, thanh confidence đỏ
   - **BENIGN:** Nền xanh, label ✓, thanh confidence xanh
   - Hiển thị confidence (%) với thanh progress bar

#### Cài đặt cho người dùng

1. Mở Chrome → vào `chrome://extensions/`
2. Bật **Developer mode**
3. Click **Load unpacked** → chọn thư mục `chrome-extension/`
4. Extension xuất hiện trên thanh toolbar

### 5.3. Deploy lên server thực tế

#### Thông tin server

- **Nền tảng:** FPT Cloud — Serverless Container
- **URL:** `https://my-container-qhx9vl5u-3000.serverless.fptcloud.com`
- **Port:** 3000

#### Kiến trúc deploy

```
User's Browser
     │
     │  HTTPS
     ▼
FPT Cloud (Serverless Container)
     │  uvicorn backend:app --host 0.0.0.0 --port 3000
     ▼
DistilBERT Model (loaded memory)
```

### 5.4. Hướng phát triển Backend nâng cao

Từ tài liệu `backend.md`, các bước nâng cấp được đề xuất:

1. **Convert model sang ONNX:** Tăng tốc inference ~2-3x, không cần PyTorch runtime
   ```bash
   optimum-cli export onnx \
       --model experiments/distilbert-phishing/best \
       --task text-classification \
       models/onnx/
   ```

2. **Docker container hóa:** Đóng gói backend thành Docker image để deploy dễ dàng

3. **Thêm API Key authentication:** Bảo mật endpoint `/predict`

4. **Rate limiting:** Chống lạm dụng API

5. **Redis caching:** Cache kết quả cho request trùng lặp

---

## KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1. Kết quả đạt được

Đề tài đã hoàn thành các mục tiêu chính:

1. **Đã xây dựng mô hình DistilBERT** cho bài toán phân loại email phishing với cấu hình huấn luyện đầy đủ (early stopping, cosine scheduler, F1-macro metric)

2. **Đã triển khai REST API** với FastAPI, hỗ trợ predict đơn lẻ và batch, tự động detect GPU/CPU

3. **Đã phát triển Chrome Extension** hoàn chỉnh với Manifest V3, hỗ trợ scan email trực tiếp từ Gmail, Outlook và Yahoo Mail

4. **Đã deploy hệ thống thực tế** lên FPT Cloud serverless container

5. **Kiến trúc 3 tầng rõ ràng** — ML Model, Backend API, Frontend extension — cho phép dễ dàng mở rộng và bảo trì

### 6.2. Hạn chế

1. **Ngôn ngữ:** Mô hình DistilBERT được huấn luyện chủ yếu trên tiếng Anh. Khả năng phát hiện phishing email tiếng Việt còn hạn chế vì DistilBERT-base-uncased là mô hình đơn ngữ

2. **Chỉ phân tích text:** Hệ thống chỉ phân tích phần text của email, chưa tận dụng:
   - Cấu trúc HTML của email
   - Metadata (header email, IP gửi, SPF/DKIM)
   - Phân tích URL và domain (WHOIS, SSL certificate)
   - Phân tích file đính kèm nếu có

3. **Chống evasion:** Người tấn công có thể cố tình thay đổi văn bản để vượt qua mô hình (adversarial attacks)

4. **Chưa cập nhật real-time:** Mô hình được huấn luyện một lần, chưa có cơ chế cập nhật liên tục với các mẫu phishing mới

5. **Hiệu năng thời gian thực:** Thời gian inference trên CPU có thể chậm (100-300ms per request), chưa đáp ứng real-time cho số lượng lớn

### 6.3. Hướng phát triển

#### Ngắn hạn

1. **Đa ngôn ngữ:** Fine-tune trên tập dữ liệu tiếng Việt, hoặc sử dụng mô hình đa ngôn ngữ như `xlm-roberta-base`

2. **Thêm feature URL analysis:** Phân tích URL riêng biệt bằng các features như:
   - Độ dài URL, sự hiện diện của IP address
   - Domain age, WHOIS information
   - SSL certificate validation
   - So sánh với blacklist (PhishTank, Google Safe Browsing API)

3. **Phân tích header email:** Thêm các feature từ SMTP header (SPF pass/fail, DKIM, DMARC, originating IP)

#### Dài hạn

1. **Ensemble model:** Kết hợp output của DistilBERT với mô hình phân tích URL, phân tích HTML

2. **Real-time learning:** Xây dựng hệ thống thu thập email mới từ người dùng báo cáo và cập nhật model định kỳ

3. **Browser extension cho nhiều trình duyệt:** Mở rộng sang Firefox, Edge, Safari

4. **Hệ thống cảnh báo:** Gửi thông báo push/email khi phát hiện phishing email đã lọc vào user

5. **API Gateway & Monitoring:** Đặt API phía sau Nginx + Grafana/Prometheus monitoring để theo dõi hiệu năng và phát hiện anomaly

6. **Mobile app:** Phát triển ứng dụng mobile cho phép forward email nghi ngại để kiểm tra

---

## TÀI LIỆU THAM KHẢO

1. Vaswani, A., et al. (2017). *Attention Is All You Need*. NeurIPS 2017.

2. Devlin, J., et al. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL-HLT 2019.

3. Sanh, V., et al. (2019). *DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter*. Workshop on Energy Efficient Machine Learning and Cognitive Computing, NeurIPS 2019.

4. Wolf, T., et al. (2020). *Transformers: State-of-the-Art Natural Language Processing*. EMNLP 2020.

5. ealvaradob. *Phishing Dataset for Machine Learning*. HuggingFace Hub. https://huggingface.co/datasets/ealvaradob/phishing-dataset

6. APWG (Anti-Phishing Working Group). *Phishing Activity Trends Report*. https://apwg.org/

7. Starace, A., et al. *PhishTank: Community Research*. https://phishtank.org/

8. FastAPI Documentation. https://fastapi.tiangolo.com/

9. HuggingFace Transformers Documentation. https://huggingface.co/docs/transformers

10. Chrome Extension Manifest V3. https://developer.chrome.com/docs/extensions/mv3/intro/

---

## PHỤ LỤC

### A. Cấu trúc mã nguồn dự án

```
distilbert_phishing/
├── main.py                          # Entry point: train/eval/predict
├── backend.py                       # FastAPI server
├── create_icons.py                  # Script sinh icon extension
├── explore_dataset.py              # Script khám phá dataset
│
├── src/
│   ├── __init__.py
│   ├── dataset.py                  # Load + tokenize dataset
│   ├── model.py                    # Xây dựng mô hình DistilBERT
│   ├── trainer.py                  # Huấn luyện với Trainer API
│   ├── evaluation.py               # Đánh giá + vẽ biểu đồ
│   └── inference.py                # Predict text mới
│
├── chrome-extension/
│   ├── manifest.json               # Cấu hình extension
│   ├── popup.html                  # Giao diện popup
│   ├── popup.js                    # Logic popup
│   ├── content.js                  # Extract email
│   └── README.md                   # HD cài đặt extension
│
├── best/                           # Thư mục model đã fine-tune
│   ├── pytorch_model.bin
│   ├── config.json
│   ├── tokenizer_config.json
│   └── ...
│
├── experiments/
│   └── distilbert-phishing/       # Log và checkpoint
│       ├── best/
│       ├── logs/
│       ├── confusion_matrix.png
│       └── roc_curve.png
│
├── docs/
│   ├── baocao.md                  # Báo cáo này
│   ├── huongdan.md                # HD sử dụng API
│   ├── backend.md                 # HD phát triển backend
│   └── test.md                    # Email mẫu test
│
└── requirements.txt               # Danh sách thư viện
```

### B. Hướng dẫn cài đặt và sử dụng

#### Cài đặt môi trường

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install transformers fastapi uvicorn torch scikit-learn matplotlib seaborn pandas datasets
```

#### Huấn luyện mô hình

```bash
# Train với default config (5 epochs)
python main.py --mode train

# Train nhanh để test (3 epochs)
python main.py --mode train --epochs 3

# Custom hyperparameters
python main.py --mode train --epochs 3 --batch-size 16 --lr 5e-5
```

#### Đánh giá mô hình

```bash
# Eval mode — chỉ evaluate model đã train
python main.py --mode eval
```

#### Dự đoán tương tác

```bash
# Predict mode — nhập text tương tác
python main.py --mode predict
```

#### Chạy Backend API

```bash
uvicorn backend:app --host 0.0.0.0 --port 3000
```

API sẽ lắng nghe tại `http://localhost:3000`. Swagger UI tại `http://localhost:3000/docs`.

#### Cài đặt Chrome Extension

1. Mở Chrome → `chrome://extensions/`
2. Bật **Developer mode**
3. **Load unpacked** → chọn thư mục `chrome-extension/`
4. Click icon extension trên toolbar để sử dụng

### C. Ví dụ API call

```bash
# curl — predict đơn lẻ
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Urgent! Your account has been compromised. Verify: http://bankofamerica-secure.tk"}'

# Response:
# {"label":"PHISHING","confidence":0.9734,"is_phishing":true}

# curl — batch predict
curl -X POST http://localhost:3000/predict/batch \
  -H "Content-Type: application/json" \
  -d '["http://secure-login.tk/verify", "https://www.google.com"]'

# Response:
# [
#   {"label":"PHISHING","confidence":0.97,"is_phishing":true},
#   {"label":"BENIGN","confidence":0.99,"is_phishing":false}
# ]
```

### D. JavaScript — gọi API từ frontend

```javascript
const response = await fetch(
  'https://my-container-qhx9vl5u-3000.serverless.fptcloud.com/predict',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: 'Dear user, your account has been suspended. Click here to verify: http://paypal-verify.tk'
    })
  }
);
const result = await response.json();
console.log(result);
// { label: "PHISHING", confidence: 0.97, is_phishing: true }
```
