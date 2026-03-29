"""
main.py — Entry point: train + evaluate DistilBERT phishing detector.

Usage:
    python main.py                        # train với default config
    python main.py --epochs 3             # train nhanh để test
    python main.py --mode eval            # chỉ evaluate model đã train
    python main.py --mode predict         # chạy demo inference
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.dataset   import prepare_datasets
from src.model     import build_model
from src.trainer   import train
from src.evaluation import evaluate_on_test
from src.inference  import load_predictor, predict_with_detail


def parse_args():
    p = argparse.ArgumentParser(description="DistilBERT Phishing Detection")
    p.add_argument("--mode",        type=str, default="train",
                   choices=["train", "eval", "predict"],
                   help="train | eval | predict")
    p.add_argument("--subset",      type=str, default="combined_reduced",
                   help="HuggingFace dataset subset")
    p.add_argument("--output-dir",  type=str, default="experiments/distilbert-phishing")
    p.add_argument("--epochs",      type=int, default=5)
    p.add_argument("--batch-size",  type=int, default=32)
    p.add_argument("--lr",          type=float, default=2e-5)
    p.add_argument("--max-len",     type=int, default=512)
    p.add_argument("--patience",    type=int, default=2,
                   help="Early stopping patience (epochs)")
    return p.parse_args()


def main():
    args = parse_args()
    best_dir = str(Path(args.output_dir) / "best")

    # ── TRAIN ────────────────────────────────────────────────────────────
    if args.mode == "train":
        # 1. Load + tokenize dataset
        dataset_dict, tokenizer = prepare_datasets(
            subset=args.subset,
            max_len=args.max_len,
        )

        # 2. Build model
        model = build_model()

        # 3. Fine-tune
        trainer = train(
            model=model,
            tokenizer=tokenizer,
            dataset_dict=dataset_dict,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            early_stopping_patience=args.patience,
        )

        # 4. Evaluate trên test set
        print("\n[INFO] Evaluating on test set...")
        evaluate_on_test(
            trainer=trainer,
            test_dataset=dataset_dict["test"],
            output_dir=args.output_dir,
        )

    # ── EVAL ONLY ────────────────────────────────────────────────────────
    elif args.mode == "eval":
        from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments

        dataset_dict, tokenizer = prepare_datasets(subset=args.subset, max_len=args.max_len)
        model = DistilBertForSequenceClassification.from_pretrained(best_dir)

        # Trainer chỉ để dùng .predict()
        eval_args = TrainingArguments(
            output_dir=args.output_dir,
            per_device_eval_batch_size=args.batch_size * 2,
            report_to="none",
        )
        trainer = Trainer(model=model, args=eval_args, tokenizer=tokenizer)
        evaluate_on_test(trainer, dataset_dict["test"], output_dir=args.output_dir)

    # ── PREDICT DEMO ─────────────────────────────────────────────────────
    elif args.mode == "predict":
        predictor = load_predictor(best_dir)

        print("Nhập text để predict (URL / email / SMS). Gõ 'quit' để thoát.\n")
        while True:
            text = input("Input > ").strip()
            if text.lower() in ("quit", "exit", "q"):
                break
            if not text:
                continue
            predict_with_detail(predictor, text)


if __name__ == "__main__":
    main()
