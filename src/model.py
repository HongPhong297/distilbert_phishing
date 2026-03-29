"""
model.py — Wrap DistilBertForSequenceClassification với config label rõ ràng.
"""

from __future__ import annotations

from transformers import DistilBertForSequenceClassification, DistilBertConfig


ID2LABEL = {0: "BENIGN", 1: "PHISHING"}
LABEL2ID = {"BENIGN": 0, "PHISHING": 1}


def build_model(model_name: str = "distilbert-base-uncased") -> DistilBertForSequenceClassification:
    """
    Khởi tạo DistilBERT fine-tune cho binary classification.

    Architecture:
        DistilBERT (6 layers, 768 hidden, 66M params)
            → [CLS] token embedding (768d)
            → Dropout(0.2)
            → Linear(768 → 2)
            → Softmax → [P(benign), P(phishing)]
    """
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    total_params = sum(p.numel() for p in model.parameters())
    trainable    = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[INFO] Model: {model_name}")
    print(f"[INFO] Total params  : {total_params:,}")
    print(f"[INFO] Trainable     : {trainable:,}")

    return model
