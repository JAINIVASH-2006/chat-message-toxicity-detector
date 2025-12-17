"""
dataset_builder_spark.py

Builds a dataset using PySpark. Two modes:
- Convert an existing CSV/Parquet (`--input`) into a cleaned Parquet/CSV dataset.
- Download a Hugging Face dataset (`--hf-dataset`) into a temporary JSONL and load it with Spark.

The output is written using Spark (Parquet or CSV). Optionally oversamples to reach `--target-size` rows.

Usage examples:
python dataset_builder_spark.py --input data/raw/jigsaw.csv --output data/datasets/jigsaw.parquet --format parquet --target-size 500000
python dataset_builder_spark.py --hf-dataset jigsaw_toxicity_pred --split train --output data/datasets/jigsaw.parquet --format parquet --target-size 200000
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, concat, lit, monotonically_increasing_id, rand
from pyspark.sql.types import StringType
import argparse
from pathlib import Path
import tempfile
import os


def normalize_text_column(df):
    # find a text column
    candidates = ['text', 'comment_text', 'tweet', 'sentence']
    for c in candidates:
        if c in df.columns:
            return df.withColumnRenamed(c, 'text')
    # fallback: first string column
    for c in df.schema.fields:
        if str(c.dataType).lower().find('string') >= 0:
            return df.withColumnRenamed(c.name, 'text')
    # if nothing, add empty text
    return df.withColumn('text', col(df.columns[0]).cast(StringType()))


def normalize_label_column(df):
    candidates = ['toxicity', 'toxicity_score', 'label', 'labels', 'target']
    for c in candidates:
        if c in df.columns:
            return df.withColumnRenamed(c, 'label')
    return df


def clean_text(df):
    df2 = df.withColumn('text', lower(regexp_replace(col('text'), r"\s+", ' ')))
    return df2


def oversample_to_target(df, target_size):
    current = df.count()
    if current >= target_size:
        return df.limit(target_size)

    # compute how many extra rows needed
    needed = target_size - current
    # sample with replacement and add small suffix to text to create variation
    sampled = df.sample(withReplacement=True, fraction=min(1.0, float(needed) / current + 0.1))
    # add an id-based suffix
    sampled = sampled.withColumn('dup_id', monotonically_increasing_id())
    sampled = sampled.withColumn('text', concat(col('text'), lit(' [dup_'), col('dup_id').cast('string'), lit(']'))).drop('dup_id')

    combined = df.unionByName(sampled)
    # if still short, repeat randomly until reach
    combined = combined.withColumn('r', rand())
    return combined.orderBy('r').limit(target_size).drop('r')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', help='Existing CSV or Parquet to convert')
    p.add_argument('--hf-dataset', help='Hugging Face dataset id to download and convert')
    p.add_argument('--split', default='train')
    p.add_argument('--output', required=True, help='Output path (parquet or csv based on --format)')
    p.add_argument('--format', default='csv', choices=['parquet', 'csv'])
    p.add_argument('--target-size', type=int, default=None, help='If provided, oversample to reach this many rows')
    args = p.parse_args()

    spark = SparkSession.builder.master('local[*]').appName('dataset-builder-spark').getOrCreate()

    input_df = None
    if args.input:
        inp = Path(args.input)
        if not inp.exists():
            raise FileNotFoundError(f'Input file not found: {inp}')
        if inp.suffix.lower() == '.csv':
            input_df = spark.read.option('header', True).option('inferSchema', True).csv(str(inp))
        else:
            input_df = spark.read.parquet(str(inp))

    elif args.hf_dataset:
        # use datasets to fetch and write a temporary JSONL which Spark can read
        try:
            from datasets import load_dataset
        except Exception as e:
            raise RuntimeError('datasets library is required to download Hugging Face datasets') from e

        tmp_dir = Path(tempfile.mkdtemp(prefix='hf_ds_'))
        tmp_file = tmp_dir / 'data.jsonl'
        print('Downloading HF dataset into temporary JSONL:', tmp_file)
        ds = load_dataset(args.hf_dataset, split=args.split)
        # write JSONL in streaming fashion
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for ex in ds:
                # convert to a simple JSON per line; Spark's json reader will parse
                import json
                f.write(json.dumps(ex, ensure_ascii=False) + '\n')

        input_df = spark.read.json(str(tmp_file))

    else:
        raise ValueError('Either --input or --hf-dataset must be provided')

    # normalize
    df = normalize_text_column(input_df)
    df = normalize_label_column(df)
    df = clean_text(df)

    if args.target_size:
        print('Current rows:', df.count())
        df = oversample_to_target(df, args.target_size)
        print('After oversample rows:', df.count())

    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    if args.format == 'parquet':
        df.write.mode('overwrite').parquet(str(outp))
    else:
        df.write.mode('overwrite').option('header', True).csv(str(outp))

    print('Wrote dataset to', outp)
    spark.stop()


if __name__ == '__main__':
    main()
