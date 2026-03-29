"""
inference.py — Dùng model đã train để predict text mới.
"""

from __future__ import annotations

from transformers import pipeline, DistilBertForSequenceClassification, DistilBertTokenizerFast


def load_predictor(model_dir: str = "experiments/distilbert-phishing/best"):
    """
    Load model đã fine-tune và trả về pipeline predict.

    Args:
        model_dir: thư mục chứa model + tokenizer đã save

    Returns:
        HuggingFace pipeline, gọi predict(text) trực tiếp
    """
    predictor = pipeline(
        "text-classification",
        model=model_dir,
        tokenizer=model_dir,
        truncation=True,
        max_length=512,
        device=0,   # GPU nếu có; đổi -1 nếu chỉ có CPU
    )
    return predictor


def predict(predictor, text: str | list[str]) -> list[dict]:
    """
    Predict một hoặc nhiều đầu vào.

    Returns:
        List of dict: [{'label': 'PHISHING', 'score': 0.97}, ...]
    """
    if isinstance(text, str):
        text = [text]
    results = predictor(text)
    return results


def predict_with_detail(predictor, text: str) -> dict:
    """
    Predict kèm in kết quả chi tiết ra console.
    """
    result = predictor(text)[0]
    label  = result["label"]
    score  = result["score"]

    status = "PHISHING" if label == "PHISHING" else "BENIGN"
    print(f"Input  : {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"Result : {status} ({score*100:.1f}% confidence)")
    print()
    return result


# ── Quick demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    model_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/distilbert-phishing/best"
    predictor = load_predictor(model_dir)

    samples = [
        # Phishing
        "http://secure-login.bankofamerica.verify-now.tk/account?id=123",
        "Your PayPal account has been limited. Verify now: http://paypa1.com/verify",
        "Congratulations! You won $1000. Click here to claim: bit.ly/win123",
        # Benign
        "https://www.google.com/search?q=python+tutorial",
        "Meeting tomorrow at 10am, please confirm your attendance.",
        "Your order #12345 has been shipped and will arrive by Friday.",
    ]

    print("=" * 60)
    print("DEMO — DistilBERT Phishing Detector")
    print("=" * 60 + "\n")

    for text in samples:
        predict_with_detail(predictor, text)
