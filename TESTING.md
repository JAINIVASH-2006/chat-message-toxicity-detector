# Testing Guide

This document describes how to test the Chat Message Toxicity Detection system.

## Prerequisites

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Verify Java is installed (required for PySpark):
```bash
java -version
```

## Running Tests

### 1. Basic Training Test

Train with default Logistic Regression model:
```bash
python train.py --num-features 500 --max-iter 50
```

**Expected Output:**
- Training completes without errors
- Model saved to `models/toxicity_model`
- IDF model saved to `models/toxicity_model_idf`
- Metrics show high accuracy (>0.90)
- Predictions saved to `output/predictions.csv`

### 2. Random Forest Model Test

Train with Random Forest:
```bash
python train.py --model-type random_forest --num-features 500 --num-trees 10
```

**Expected Output:**
- Model trains successfully
- Accuracy may be slightly different from Logistic Regression
- All files saved correctly

### 3. Prediction Tests

#### Test with Example Messages
```bash
python predict.py --num-features 500
```

**Expected Output:**
- 6 example messages processed
- Each message classified as TOXIC or NON-TOXIC
- Confidence scores provided for each prediction

#### Test with Custom Messages
```bash
python predict.py --num-features 500 --message "You're amazing!" "I hate you"
```

**Expected Output:**
- "You're amazing!" → NON-TOXIC (high confidence)
- "I hate you" → TOXIC (high confidence)

#### Test with CSV File
```bash
python predict.py --num-features 500 --file data/test_data.csv
```

**Expected Output:**
- All messages from test file processed
- Predictions displayed with confidence scores

### 4. Example Usage Script Test

Run all examples:
```bash
python example_usage.py
```

**Expected Output:**
- Basic usage example completes
- Custom preprocessing demonstration works
- Model comparison shows metrics for both models
- All examples complete successfully

## Validation Checklist

Use this checklist to validate the system:

- [ ] Training script runs without errors
- [ ] Both Logistic Regression and Random Forest models train successfully
- [ ] Model files are saved to `models/` directory
- [ ] IDF model files are saved with `_idf` suffix
- [ ] Prediction script loads models correctly
- [ ] Predictions are accurate for obviously toxic messages
- [ ] Predictions are accurate for obviously non-toxic messages
- [ ] Confidence scores are reasonable (>50% for clear cases)
- [ ] Example usage script demonstrates all features
- [ ] Output files are generated in `output/` directory
- [ ] No security vulnerabilities reported by CodeQL

## Performance Benchmarks

Typical performance on sample datasets:

**Training:**
- Time: ~1-2 minutes for Logistic Regression
- Time: ~2-3 minutes for Random Forest
- Memory: ~2GB driver and executor memory

**Prediction:**
- Time: ~30-60 seconds for 30 messages
- Latency: ~1-2 seconds per message

**Accuracy:**
- Logistic Regression: >95% on test set
- Random Forest: >90% on test set

## Troubleshooting Tests

### Issue: Training takes too long
**Solution:** Reduce num-features parameter
```bash
python train.py --num-features 200
```

### Issue: Out of memory errors
**Solution:** Edit spark configuration in train.py:
```python
.config("spark.driver.memory", "1g")
.config("spark.executor.memory", "1g")
```

### Issue: Prediction accuracy is poor
**Solution:** Ensure you're using the same num-features for training and prediction:
```bash
# Train with 500 features
python train.py --num-features 500

# Predict with same 500 features
python predict.py --num-features 500
```

### Issue: IDF model not found
**Solution:** Ensure training completed successfully and IDF model was saved:
```bash
ls -la models/toxicity_model_idf/
```

## Test Data Format

When creating custom test data, use this CSV format:

```csv
message,label
"Your positive message here",0
"Your toxic message here",1
```

- Column 1: `message` - The text to classify
- Column 2: `label` - 0 for non-toxic, 1 for toxic

## Continuous Testing

For continuous development, run this test sequence:

```bash
# 1. Clean previous results
rm -rf models/toxicity_model* output/*

# 2. Train model
python train.py --num-features 500

# 3. Test predictions
python predict.py --num-features 500 --message "Test message"

# 4. Run full example suite
python example_usage.py
```

## Integration Testing

To test the system in a production-like environment:

1. Use larger datasets (1000+ samples)
2. Test with real-world chat messages
3. Measure prediction latency
4. Monitor memory usage
5. Test model reloading after restart

## Success Criteria

The system passes testing if:

1. ✅ Training completes without errors for both model types
2. ✅ Predictions are consistent across multiple runs
3. ✅ Accuracy is >90% on test set
4. ✅ No security vulnerabilities detected
5. ✅ All example scripts run successfully
6. ✅ Model persistence works correctly (save/load)
7. ✅ Documentation is clear and accurate

## Reporting Issues

If you encounter issues during testing:

1. Check that all dependencies are installed
2. Verify Java 8+ is available
3. Ensure sufficient memory is available
4. Review error messages carefully
5. Check that file paths are correct
6. Verify CSV file format matches expected format
7. Open an issue on GitHub with error details
