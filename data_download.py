"""
data_download.py

Downloads a large toxicity dataset using Hugging Face `datasets` and writes to CSV or Parquet.

Usage examples:
python data_download.py --dataset jigsaw_toxicity_pred --out data/raw/jigsaw.csv --max-examples 200000
python data_download.py --dataset civil_comments --out data/raw/civil.parquet --format parquet
"""
import argparse
from datasets import load_dataset
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def download_and_save(dataset_name: str, split: str, out_path: Path, fmt: str, max_examples: int | None):
    print(f"Loading dataset {dataset_name} split={split} (will download if needed)...")
    ds = load_dataset(dataset_name, split=split)
    if max_examples:
        ds = ds.select(range(min(max_examples, len(ds))))
    print(f"Dataset loaded: {len(ds)} rows")

    # Normalize known field names—we keep `text` and `toxicity` or `label`
    def row_map(ex):
        if 'text' in ex:
            text = ex['text']
        elif 'comment_text' in ex:
            text = ex['comment_text']
        elif 'tweet' in ex:
            text = ex['tweet']
        else:
            # try common fields
            # fallback: first string field
            for k, v in ex.items():
                if isinstance(v, str) and v.strip():
                    text = v
                    break
            else:
                text = ''
        # find a toxicity score/label if available
        label = None
        for candidate in ('toxicity', 'toxicity_score', 'label', 'labels', 'target'):
            if candidate in ex:
                label = ex[candidate]
                break
        return {'text': text, 'label': label}

    # Convert using pandas in streaming fashion
    rows = []
    for ex in tqdm(ds, total=len(ds), desc='Converting'):
        rows.append(row_map(ex))
    df = pd.DataFrame(rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == 'csv':
        df.to_csv(out_path, index=False)
    else:
        df.to_parquet(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', required=True, help='Hugging Face dataset name, e.g. jigsaw_toxicity_pred or civil_comments')
    p.add_argument('--split', default='train', help='Dataset split to download')
    p.add_argument('--out', required=True, help='Output path (csv or parquet)')
    p.add_argument('--format', default='csv', choices=['csv', 'parquet'])
    p.add_argument('--max-examples', type=int, default=None, help='Limit number of examples to download (for quick tests)')
    args = p.parse_args()

    download_and_save(args.dataset, args.split, Path(args.out), args.format, args.max_examples)
