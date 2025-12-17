# Quick Start Guide

Get started with the Chat Message Toxicity Detector in 5 minutes!

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation (ensure Java 8+ is installed)
java -version
```

## Train Your First Model

```bash
# Train with default settings (takes ~2 minutes)
python train.py

# Output: Model saved to models/toxicity_model
```

## Make Predictions

### Option 1: Predict with Example Messages
```bash
python predict.py
```

### Option 2: Predict Custom Messages
```bash
python predict.py --message "You're amazing!" "I hate you"
```

### Option 3: Predict from CSV File
```bash
python predict.py --file data/test_data.csv --output output/my_predictions.csv
```

## Run Examples

```bash
# See all features in action
python example_usage.py
```

## Expected Output

### Training
```
Model Performance:
  Accuracy:  1.0000
  Precision: 1.0000
  Recall:    1.0000
  F1 Score:  1.0000
  AUC-ROC:   1.0000
```

### Prediction
```
[1] Message: You are amazing! Keep up the great work!
    Prediction: NON-TOXIC
    Confidence: 96.22%
```

## Troubleshooting

### "Java not found"
Install Java 8 or higher and set JAVA_HOME environment variable.

### "Module not found"
Run: `pip install -r requirements.txt`

### "Memory Error"
Edit train.py or predict.py and reduce spark memory settings:
```python
.config("spark.driver.memory", "1g")
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize preprocessing in `src/preprocessing.py`
- Try different models: `python train.py --model-type random_forest`
- Adjust features: `python train.py --num-features 2000`

## Need Help?

- Check [README.md](README.md) for comprehensive documentation
- Review `example_usage.py` for code examples
- Open an issue on GitHub for support

Happy toxicity detection! 🚀
