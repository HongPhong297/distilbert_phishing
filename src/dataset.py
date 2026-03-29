"""
dataset.py — Load và tokenize ealvaradob/phishing-dataset cho DistilBERT.
"""

from __future__ import annotations

from datasets import load_dataset, Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizerFast
import pandas as pd


MODEL_NAME = "distilbert-base-uncased"
MAX_LEN    = 512


def load_raw_dataset(subset: str = "combined_reduced") -> pd.DataFrame:
    """
    Load dataset từ HuggingFace Hub.

    subset options:
        "urls"              — chỉ URLs (~800k, nặng)
        "combined_reduced"  — URL + Email + SMS, balanced (khuyến nghị)
        "combined_full"     — toàn bộ, URL chiếm 97%

    Returns:
        DataFrame với columns: ['text', 'label']  (label: 0=benign, 1=phishing)
    """
    print(f"[INFO] Loading dataset: ealvaradob/phishing-dataset / {subset} ...")
    raw = load_dataset(
        "ealvaradob/phishing-dataset",
        subset,
        trust_remote_code=True,
    )
    df = raw["train"].to_pandas()
    print(f"[INFO] Total rows: {len(df):,}")
    print(f"[INFO] Label distribution:\n{df['label'].value_counts().to_string()}")
    return df


def split_dataset(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.10,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chia train / val / test với stratify.

    Tỉ lệ: 75% train · 10% val · 15% test
    """
    # Bước 1: tách test ra trước
    train_val, test = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"],
    )
    # Bước 2: tách val từ phần còn lại
    relative_val = val_size / (1.0 - test_size)
    train, val = train_test_split(
        train_val,
        test_size=relative_val,
        random_state=random_state,
        stratify=train_val["label"],
    )

    print(f"[INFO] Split → train: {len(train):,} | val: {len(val):,} | test: {len(test):,}")
    for name, split in [("train", train), ("val", val), ("test", test)]:
        vc = split["label"].value_counts()
        print(f"         {name}: benign={vc.get(0,0):,}  phishing={vc.get(1,0):,}")

    return train, val, test


def tokenize_dataset(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    tokenizer: DistilBertTokenizerFast,
    max_len: int = MAX_LEN,
) -> DatasetDict:
    """
    Tokenize 3 splits và trả về HuggingFace DatasetDict.

    Mỗi sample:
        input_ids      : [CLS] token_ids [SEP] [PAD...]
        attention_mask : 1 cho token thật, 0 cho PAD
        labels         : 0 hoặc 1
    """
    def _tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=max_len,
        )

    splits = {}
    for name, df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        ds = Dataset.from_pandas(df[["text", "label"]].reset_index(drop=True))
        ds = ds.map(_tokenize, batched=True, batch_size=512)
        ds = ds.rename_column("label", "labels")
        ds.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
        splits[name] = ds
        print(f"[INFO] Tokenized {name}: {len(ds):,} samples")

    return DatasetDict(splits)


def prepare_datasets(
    subset: str = "combined_reduced",
    max_len: int = MAX_LEN,
    test_size: float = 0.15,
    val_size: float = 0.10,
) -> tuple[DatasetDict, DistilBertTokenizerFast]:
    """
    Entry point: load → split → tokenize.

    Returns:
        dataset_dict : DatasetDict với keys train / val / test
        tokenizer    : tokenizer đã load (cần lưu cùng model)
    """
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

    df = load_raw_dataset(subset)
    train_df, val_df, test_df = split_dataset(df, test_size, val_size)
    dataset_dict = tokenize_dataset(train_df, val_df, test_df, tokenizer, max_len)

    return dataset_dict, tokenizer
