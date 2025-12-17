# Chat Message Toxicity Detector

A scalable machine learning system built with Python and Apache Spark (PySpark) to detect toxic and abusive messages in chat conversations. The system uses advanced text preprocessing, TF-IDF feature extraction, and machine learning classification to identify harmful content efficiently.

## Features

- **Data Preprocessing**: Text cleaning, tokenization, and stop word removal
- **TF-IDF Feature Extraction**: Converts text into numerical features using HashingTF and IDF
- **Machine Learning Models**: Support for Logistic Regression and Random Forest classifiers
- **Scalable Processing**: Built on Apache Spark for handling large-scale data
- **Model Evaluation**: Comprehensive metrics including accuracy, precision, recall, F1-score, and AUC-ROC
- **Easy Prediction**: Simple interface for predicting toxicity of new messages

## Project Structure

```
chat-message-toxicity-detector/
├── data/
│   ├── train_data.csv          # Training dataset
│   └── test_data.csv           # Test dataset
├── src/
│   ├── __init__.py             # Package initializer
│   ├── preprocessing.py        # Text preprocessing and feature extraction
│   └── model.py                # ML model training and evaluation
├── models/                      # Saved trained models (generated)
├── output/                      # Prediction results and metrics (generated)
├── train.py                    # Main training script
├── predict.py                  # Prediction/inference script
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Java 8 or higher (required for PySpark)
- Apache Spark 3.0 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JAINIVASH-2006/chat-message-toxicity-detector.git
cd chat-message-toxicity-detector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dataset Format

The dataset should be in CSV format with two columns:
- `message`: The chat message text
- `label`: Binary label (0 for non-toxic, 1 for toxic)

Example:
```csv
message,label
"You're doing great! Keep it up!",0
"I hate you so much you idiot",1
```

## Usage

### Training the Model

Train a model using the default settings:
```bash
python train.py
```

Train with custom parameters:
```bash
python train.py --train-data data/train_data.csv \
                --test-data data/test_data.csv \
                --model-type logistic_regression \
                --num-features 1000 \
                --max-iter 100 \
                --model-path models/toxicity_model \
                --output-dir output
```

#### Training Parameters

- `--train-data`: Path to training CSV file (default: `data/train_data.csv`)
- `--test-data`: Path to test CSV file (default: `data/test_data.csv`)
- `--model-type`: Model type - `logistic_regression` or `random_forest` (default: `logistic_regression`)
- `--num-features`: Number of TF-IDF features (default: 1000)
- `--max-iter`: Maximum iterations for Logistic Regression (default: 100)
- `--num-trees`: Number of trees for Random Forest (default: 20)
- `--model-path`: Path to save trained model (default: `models/toxicity_model`)
- `--output-dir`: Directory to save results (default: `output`)

### Making Predictions

#### Predict Single or Multiple Messages

```bash
python predict.py --model-path models/toxicity_model \
                  --message "You are amazing!" "I hate you"
```

#### Predict from CSV File

```bash
python predict.py --model-path models/toxicity_model \
                  --file data/new_messages.csv \
                  --output output/predictions.csv
```

#### Run with Example Messages

```bash
python predict.py --model-path models/toxicity_model
```

#### Prediction Parameters

- `--model-path`: Path to trained model (default: `models/toxicity_model`)
- `--model-type`: Model type used during training (default: `logistic_regression`)
- `--num-features`: Number of features (must match training) (default: 1000)
- `--message`: One or more messages to predict
- `--file`: CSV file with messages to predict
- `--output`: Path to save predictions CSV

## How It Works

### 1. Data Preprocessing

The system performs the following preprocessing steps:

- **Text Cleaning**: Converts to lowercase, removes URLs, emails, special characters
- **Tokenization**: Splits text into individual words
- **Stop Word Removal**: Removes common words (e.g., "the", "is", "and")
- **TF-IDF Feature Extraction**: Converts text to numerical features using:
  - **HashingTF**: Maps terms to feature indices
  - **IDF**: Weighs features by their importance

### 2. Model Training

The system supports two classification algorithms:

- **Logistic Regression**: Fast, interpretable binary classifier
- **Random Forest**: Ensemble method with multiple decision trees

### 3. Evaluation Metrics

Models are evaluated using:
- **Accuracy**: Overall correctness
- **Precision**: Proportion of positive predictions that are correct
- **Recall**: Proportion of actual positives correctly identified
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the ROC curve

### 4. Prediction

The trained model can classify new messages as:
- **Non-toxic (0)**: Safe, appropriate messages
- **Toxic (1)**: Harmful, abusive messages

Each prediction includes confidence scores for both classes.

## Example Output

### Training Output

```
=== Training LOGISTIC_REGRESSION Model ===
Training logistic_regression model...
Model training completed!

=== Evaluating Model ===

Model Performance:
  Accuracy:  0.9333
  Precision: 0.9342
  Recall:    0.9333
  F1 Score:  0.9334
  AUC-ROC:   0.9778

Sample Predictions:
+--------------------------------------------------+-----+----------+--------------------+
|                                           message|label|prediction|         probability|
+--------------------------------------------------+-----+----------+--------------------+
|                              You're amazing!    0|    0|       0.0|[0.9234, 0.0766]    |
|                       I hate your stupid face   1|    1|       1.0|[0.0891, 0.9109]    |
+--------------------------------------------------+-----+----------+--------------------+
```

### Prediction Output

```
================================================================================
PREDICTIONS
================================================================================

[1] Message: You are amazing! Keep up the great work!
    Prediction: NON-TOXIC
    Confidence: 95.23%
    Probabilities: [Non-toxic: 0.9523, Toxic: 0.0477]

[2] Message: I hate you and hope you fail
    Prediction: TOXIC
    Confidence: 91.84%
    Probabilities: [Non-toxic: 0.0816, Toxic: 0.9184]
================================================================================
```

## Technical Details

### Technologies Used

- **PySpark**: Distributed data processing and machine learning
- **PySpark MLlib**: Machine learning library for classification
- **Python**: Core programming language

### Key Components

1. **TextPreprocessor** (`src/preprocessing.py`):
   - Handles all text preprocessing operations
   - Creates TF-IDF feature vectors
   - Reusable for training and prediction

2. **ToxicityClassifier** (`src/model.py`):
   - Manages model creation, training, and evaluation
   - Supports multiple model types
   - Provides comprehensive evaluation metrics

3. **Training Pipeline** (`train.py`):
   - Orchestrates data loading, preprocessing, training, and evaluation
   - Saves trained models and results
   - Configurable via command-line arguments

4. **Prediction Pipeline** (`predict.py`):
   - Loads trained models
   - Processes new messages
   - Provides user-friendly output

## Performance Considerations

- **Scalability**: Built on Spark for distributed processing of large datasets
- **Memory**: Default configuration uses 2GB driver and executor memory
- **Features**: 1000 TF-IDF features by default (adjustable)
- **Models**: Logistic Regression is faster; Random Forest may be more accurate

## Customization

### Adding Custom Preprocessing

Modify `src/preprocessing.py` to add custom text cleaning steps:

```python
def clean_text(text):
    # Add your custom preprocessing here
    text = text.lower()
    # ... additional steps
    return text
```

### Using Different Models

The system can be extended to support additional PySpark MLlib classifiers:

```python
from pyspark.ml.classification import NaiveBayes

# Add to ToxicityClassifier.create_model()
if self.model_type == "naive_bayes":
    self.model = NaiveBayes(...)
```

## Troubleshooting

### Java Not Found
Ensure Java 8+ is installed and `JAVA_HOME` is set:
```bash
export JAVA_HOME=/path/to/java
```

### Memory Issues
Adjust Spark memory configuration in the scripts:
```python
.config("spark.driver.memory", "4g")
.config("spark.executor.memory", "4g")
```

### PySpark Installation Issues
Try installing with specific version:
```bash
pip install pyspark==3.3.0
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available for educational and research purposes.

## Contact

For questions or support, please open an issue on the GitHub repository.

## Acknowledgments

- Built with Apache Spark MLlib
- Inspired by the need for safe online communication
- Sample datasets created for demonstration purposes
