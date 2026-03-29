"""
evaluation.py — Đánh giá model trên test set và vẽ biểu đồ.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from transformers import Trainer


def evaluate_on_test(trainer: Trainer, test_dataset, output_dir: str = "experiments") -> dict:
    """
    Chạy predict trên test set, in full classification report,
    vẽ confusion matrix + ROC curve.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Running prediction on test set...")
    pred_output = trainer.predict(test_dataset)

    logits = pred_output.predictions          # (N, 2)
    labels = pred_output.label_ids            # (N,)
    preds  = np.argmax(logits, axis=1)
    probs  = _softmax(logits)[:, 1]           # P(phishing)

    # ── Classification report ──────────────────────────────────────────
    print("\n===== TEST RESULTS =====")
    print(classification_report(
        labels, preds,
        target_names=["BENIGN", "PHISHING"],
        digits=4,
    ))
    print(f"ROC-AUC : {roc_auc_score(labels, probs):.4f}")

    # ── Confusion matrix ───────────────────────────────────────────────
    cm_path = _plot_confusion_matrix(labels, preds, output_dir)
    print(f"[INFO] Saved: {cm_path}")

    # ── ROC curve ─────────────────────────────────────────────────────
    roc_path = _plot_roc_curve(labels, probs, output_dir)
    print(f"[INFO] Saved: {roc_path}")

    return {
        "preds" : preds,
        "probs" : probs,
        "labels": labels,
    }


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def _plot_confusion_matrix(labels, preds, output_dir: Path) -> Path:
    cm = confusion_matrix(labels, preds)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["BENIGN", "PHISHING"],
        yticklabels=["BENIGN", "PHISHING"],
        ax=ax,
    )
    ax.set_title("Confusion Matrix — DistilBERT Phishing Detection")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    path = output_dir / "confusion_matrix.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_roc_curve(labels, probs, output_dir: Path) -> Path:
    fpr, tpr, _ = roc_curve(labels, probs)
    auc = roc_auc_score(labels, probs)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(fpr, tpr, color="darkorange", lw=2, label=f"AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], "--", color="navy", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — DistilBERT Phishing Detection")
    ax.legend(loc="lower right")
    path = output_dir / "roc_curve.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
