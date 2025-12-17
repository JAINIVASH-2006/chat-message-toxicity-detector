# Chat Message Toxicity Detector — Project Scaffold

This repository scaffolds a toxicity-detection project that:
- downloads large public toxicity datasets (Hugging Face / Jigsaw / Civil Comments),
- preprocesses them using PySpark (so jobs appear in the Spark Web UI),
- exposes a small Flask web app to trigger processing and serve predictions.

Important: This scaffold does NOT generate toxic messages itself in helper outputs. It uses publicly available datasets via the `datasets` library to obtain real annotated samples.

## Requirements
- Python 3.9+ (use a venv)
- Java 8+ (for PySpark)

Install dependencies (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r "d:\spark main\requirements.txt"
```

## Quick start
1. Download a dataset (Jigsaw / civil_comments) as CSV/Parquet:

```powershell
python data_download.py --dataset jigsaw_toxicity_pred --out data/raw/jigsaw.csv --max-examples 200000
```

2. Preprocess with Spark (this will start a local SparkContext and show the job in the Spark UI at http://localhost:4040):

```powershell
python spark_job.py --input data/raw/jigsaw.csv --output data/processed/jigsaw.parquet --num-partitions 8
```

3. Run the web app (Flask):

```powershell
python app.py
```

Open `http://127.0.0.1:5000` for the simple web UI. Use the `/run-spark` endpoint to trigger preprocessing via the web app.

## Notes
- If you prefer Kaggle Jigsaw CSVs, download them manually and set `--input` to the file path.
- Spark Web UI appears on `localhost:4040` while a SparkContext is active.
- This scaffold focuses on data and integration; model training and production deployment are next steps.

## Spark Web UI — connect from the dashboard

The dashboard includes an "Open Spark UI" button and an option to embed the Spark Web UI inline.

How to connect:

- Start a Spark job (for example by running `spark_job.py` or triggering a job from the web app). While the SparkContext is active, the Web UI is available at http://localhost:4040 on the same machine.
- From the dashboard (`http://127.0.0.1:5000`) click "Open Spark UI" to open the Spark UI in a new tab.
- If you prefer embedding the Spark UI inside the dashboard, click "Embed Spark UI" — the dashboard will set an iframe to `http://localhost:4040`. Note:
	- Some browser/security settings or Spark's response headers may prevent framing. If the iframe stays blank, open the Spark UI in a new tab instead.
	- Embedding works only when both services run on the same laptop (localhost). If Spark runs on a remote cluster, you must expose the Spark UI URL and update the iframe URL.

Security and practical notes:
- The dashboard runs on `localhost:5000` by default; Spark uses `localhost:4040`. Both are on your machine and can communicate locally.
- Avoid exposing the Spark UI or the Flask app to the public internet without proper authentication.

If you'd like, I can add a small reverse-proxy endpoint in the Flask app that forwards Spark UI requests (useful when embedding), but that is more advanced and needs careful handling of headers and streamed responses. The iframe approach is simpler and works in most local setups.
