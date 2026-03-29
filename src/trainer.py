"""
trainer.py — Fine-tune DistilBERT dùng HuggingFace Trainer API.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from transformers import (
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)


def compute_metrics(eval_pred) -> dict[str, float]:
    """
    Metrics dùng trong Trainer.evaluate() và log sau mỗi epoch.
    Dùng macro average để đánh giá cân bằng cả 2 class.
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    probs = softmax(logits)[:, 1]   # P(phishing)

    return {
        "accuracy" : float(accuracy_score(labels, preds)),
        "f1_macro" : float(f1_score(labels, preds, average="macro",    zero_division=0)),
        "precision": float(precision_score(labels, preds, average="macro", zero_division=0)),
        "recall"   : float(recall_score(labels, preds, average="macro",    zero_division=0)),
        "roc_auc"  : float(roc_auc_score(labels, probs)),
    }


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def build_training_args(
    output_dir: str = "experiments/distilbert-phishing",
    epochs: int = 5,
    batch_size: int = 32,
    learning_rate: float = 2e-5,
    warmup_ratio: float = 0.1,
    weight_decay: float = 0.01,
) -> TrainingArguments:
    """
    Cấu hình training:
        - evaluation + save sau mỗi epoch
        - load_best_model_at_end → tự load checkpoint tốt nhất
        - fp16=True nếu có GPU (tăng tốc ~2x, giảm RAM)
    """
    return TrainingArguments(
        output_dir=output_dir,

        # Epochs & batch
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size * 2,

        # Optimizer
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        lr_scheduler_type="cosine",

        # Evaluation
        eval_strategy="epoch",
        save_strategy="epoch",
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        load_best_model_at_end=True,

        # Logging
        logging_dir=f"{output_dir}/logs",
        logging_steps=100,
        report_to="none",   # đổi sang "tensorboard" nếu muốn visualize

        # Performance
        fp16=True,          # tắt nếu không có GPU: fp16=False
        dataloader_num_workers=2,
        save_total_limit=2, # chỉ giữ 2 checkpoint gần nhất
    )


def train(
    model,
    tokenizer,
    dataset_dict,
    output_dir: str = "experiments/distilbert-phishing",
    epochs: int = 5,
    batch_size: int = 32,
    learning_rate: float = 2e-5,
    early_stopping_patience: int = 2,
) -> Trainer:
    """
    Chạy fine-tuning và trả về Trainer (để dùng evaluate/predict sau).

    Early stopping: dừng nếu val f1_macro không cải thiện sau N epochs.
    """
    training_args = build_training_args(
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
    )

    # DataCollator tự động padding dynamic trong batch → tiết kiệm memory
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["val"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)
        ],
    )

    print("[INFO] Starting fine-tuning...")
    trainer.train()

    # Lưu model + tokenizer tốt nhất
    best_dir = Path(output_dir) / "best"
    trainer.save_model(str(best_dir))
    tokenizer.save_pretrained(str(best_dir))
    print(f"[INFO] Best model saved to: {best_dir}")

    return trainer
