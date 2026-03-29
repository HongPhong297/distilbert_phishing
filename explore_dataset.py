"""
explore_dataset.py — Tải và khám phá dataset phishing.
"""

from datasets import load_dataset


def main():
    print("[INFO] Loading dataset: ealvaradob/phishing-dataset / combined_reduced")
    raw = load_dataset("ealvaradob/phishing-dataset", "combined_reduced", trust_remote_code=True)
    
    df = raw["train"].to_pandas()
    
    print(f"\n=== Dataset Info ===")
    print(f"Total rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print(f"\n=== Label Distribution ===")
    print(df['label'].value_counts())
    print(f"\nLabel: 0 = benign, 1 = phishing")
    
    print(f"\n=== Sample Data (5 benign) ===")
    print(df[df['label'] == 0]['text'].head(5).to_string())
    
    print(f"\n=== Sample Data (5 phishing) ===")
    print(df[df['label'] == 1]['text'].head(5).to_string())


if __name__ == "__main__":
    main()
