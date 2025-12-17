"""
Main Training Script
Trains the toxicity detection model using PySpark
"""

import argparse
import os
from pyspark.sql import SparkSession
from src.preprocessing import TextPreprocessor
from src.model import ToxicityClassifier


def create_spark_session(app_name="ToxicityDetector"):
    """
    Create and configure Spark session
    
    Args:
        app_name (str): Name of the Spark application
        
    Returns:
        SparkSession: Configured Spark session
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def load_data(spark, train_path, test_path):
    """
    Load training and test data
    
    Args:
        spark (SparkSession): Spark session
        train_path (str): Path to training data
        test_path (str): Path to test data
        
    Returns:
        tuple: Training and test DataFrames
    """
    print(f"Loading training data from {train_path}")
    train_df = spark.read.csv(train_path, header=True, inferSchema=True)
    
    print(f"Loading test data from {test_path}")
    test_df = spark.read.csv(test_path, header=True, inferSchema=True)
    
    print(f"Training samples: {train_df.count()}")
    print(f"Test samples: {test_df.count()}")
    
    return train_df, test_df


def preprocess_data(train_df, test_df, num_features=1000):
    """
    Preprocess training and test data
    
    Args:
        train_df (DataFrame): Training DataFrame
        test_df (DataFrame): Test DataFrame
        num_features (int): Number of TF-IDF features
        
    Returns:
        tuple: Preprocessed training and test DataFrames
    """
    print("\n=== Preprocessing Data ===")
    preprocessor = TextPreprocessor()
    
    # Preprocess training data
    print("Preprocessing training data...")
    train_processed = preprocessor.full_pipeline(train_df, text_column="message", num_features=num_features)
    
    # Preprocess test data using the same preprocessor
    print("Preprocessing test data...")
    test_processed = preprocessor.preprocess_dataframe(test_df, text_column="message")
    test_processed = preprocessor.tokenize_text(test_processed, input_col="cleaned_text", output_col="words")
    test_processed = preprocessor.remove_stop_words(test_processed, input_col="words", output_col="filtered_words")
    
    # Apply the same TF-IDF model learned from training data
    if preprocessor.hashing_tf is not None and preprocessor.idf_model is not None:
        test_processed = preprocessor.hashing_tf.transform(test_processed)
        test_processed = preprocessor.idf_model.transform(test_processed)
    else:
        raise ValueError("TF-IDF models not initialized. Ensure full_pipeline was called on training data.")
    
    return train_processed, test_processed, preprocessor


def train_model(train_df, model_type="logistic_regression", **model_params):
    """
    Train the toxicity classification model
    
    Args:
        train_df (DataFrame): Preprocessed training DataFrame
        model_type (str): Type of model to train
        **model_params: Additional model parameters
        
    Returns:
        ToxicityClassifier: Trained classifier
    """
    print(f"\n=== Training {model_type.upper()} Model ===")
    
    classifier = ToxicityClassifier(model_type=model_type)
    classifier.create_model(**model_params)
    classifier.train(train_df)
    
    return classifier


def evaluate_model(classifier, test_df):
    """
    Evaluate the trained model
    
    Args:
        classifier (ToxicityClassifier): Trained classifier
        test_df (DataFrame): Preprocessed test DataFrame
    """
    print("\n=== Evaluating Model ===")
    
    # Make predictions
    predictions = classifier.predict(test_df)
    
    # Calculate metrics
    metrics = classifier.evaluate(predictions)
    
    # Print results
    print("\nModel Performance:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")
    print(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
    
    # Show some sample predictions
    print("\nSample Predictions:")
    predictions.select("message", "label", "prediction", "probability").show(10, truncate=50)
    
    return predictions, metrics


def save_results(predictions, metrics, output_dir="output"):
    """
    Save predictions and metrics
    
    Args:
        predictions (DataFrame): Predictions DataFrame
        metrics (dict): Evaluation metrics
        output_dir (str): Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save metrics
    metrics_path = os.path.join(output_dir, "metrics.txt")
    with open(metrics_path, 'w') as f:
        f.write("Model Evaluation Metrics\n")
        f.write("=" * 40 + "\n")
        for metric_name, metric_value in metrics.items():
            f.write(f"{metric_name.capitalize()}: {metric_value:.4f}\n")
    
    print(f"\nMetrics saved to {metrics_path}")
    
    # Save predictions
    predictions_path = os.path.join(output_dir, "predictions.csv")
    predictions.select("message", "label", "prediction").coalesce(1).write.csv(
        predictions_path, header=True, mode="overwrite"
    )
    print(f"Predictions saved to {predictions_path}")


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train Toxicity Detection Model")
    parser.add_argument("--train-data", type=str, default="data/train_data.csv",
                        help="Path to training data")
    parser.add_argument("--test-data", type=str, default="data/test_data.csv",
                        help="Path to test data")
    parser.add_argument("--model-type", type=str, default="logistic_regression",
                        choices=["logistic_regression", "random_forest"],
                        help="Type of model to train")
    parser.add_argument("--num-features", type=int, default=1000,
                        help="Number of TF-IDF features")
    parser.add_argument("--max-iter", type=int, default=100,
                        help="Maximum iterations for Logistic Regression")
    parser.add_argument("--num-trees", type=int, default=20,
                        help="Number of trees for Random Forest")
    parser.add_argument("--model-path", type=str, default="models/toxicity_model",
                        help="Path to save the trained model")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Directory to save results")
    
    args = parser.parse_args()
    
    # Create Spark session
    print("=== Initializing Spark Session ===")
    spark = create_spark_session()
    
    try:
        # Load data
        train_df, test_df = load_data(spark, args.train_data, args.test_data)
        
        # Preprocess data
        train_processed, test_processed, preprocessor = preprocess_data(
            train_df, test_df, num_features=args.num_features
        )
        
        # Train model
        model_params = {}
        if args.model_type == "logistic_regression":
            model_params['max_iter'] = args.max_iter
        elif args.model_type == "random_forest":
            model_params['num_trees'] = args.num_trees
        
        classifier = train_model(train_processed, model_type=args.model_type, **model_params)
        
        # Evaluate model
        predictions, metrics = evaluate_model(classifier, test_processed)
        
        # Save model and preprocessor
        print(f"\n=== Saving Model and Preprocessor ===")
        os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
        classifier.save_model(args.model_path)
        
        # Save IDF model for use during prediction
        idf_model_path = args.model_path + "_idf"
        preprocessor.save_idf_model(idf_model_path)
        
        # Save results
        save_results(predictions, metrics, args.output_dir)
        
        print("\n=== Training Complete ===")
        
    finally:
        # Stop Spark session
        spark.stop()


if __name__ == "__main__":
    main()
