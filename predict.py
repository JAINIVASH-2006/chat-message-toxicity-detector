"""
Prediction Script
Makes predictions on new messages using trained model
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.ml.classification import LogisticRegressionModel, RandomForestClassificationModel
from pyspark.ml.feature import HashingTF
from src.preprocessing import TextPreprocessor


def create_spark_session(app_name="ToxicityPredictor"):
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
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def load_model(model_path, model_type="logistic_regression"):
    """
    Load trained model
    
    Args:
        model_path (str): Path to the saved model
        model_type (str): Type of model
        
    Returns:
        Model: Loaded model
    """
    if model_type == "logistic_regression":
        model = LogisticRegressionModel.load(model_path)
    elif model_type == "random_forest":
        model = RandomForestClassificationModel.load(model_path)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    print(f"Model loaded from {model_path}")
    return model


def load_preprocessor(idf_model_path, num_features=1000):
    """
    Load and initialize preprocessor with saved IDF model
    
    Args:
        idf_model_path (str): Path to saved IDF model
        num_features (int): Number of TF-IDF features
        
    Returns:
        TextPreprocessor: Initialized preprocessor
    """
    preprocessor = TextPreprocessor()
    
    # Initialize HashingTF with same parameters as training
    preprocessor.hashing_tf = HashingTF(
        inputCol="filtered_words",
        outputCol="raw_features",
        numFeatures=num_features
    )
    
    # Load the saved IDF model
    preprocessor.load_idf_model(idf_model_path)
    
    return preprocessor


def predict_messages(spark, model, messages, preprocessor):
    """
    Predict toxicity for a list of messages
    
    Args:
        spark (SparkSession): Spark session
        model: Trained model
        messages (list): List of messages to predict
        preprocessor (TextPreprocessor): Initialized preprocessor with IDF model
        
    Returns:
        DataFrame: Predictions DataFrame
    """
    # Create DataFrame from messages
    schema = StructType([StructField("message", StringType(), True)])
    messages_df = spark.createDataFrame([(msg,) for msg in messages], schema)
    
    # Preprocess messages using the loaded preprocessor
    processed_df = preprocessor.preprocess_dataframe(messages_df, text_column="message")
    processed_df = preprocessor.tokenize_text(processed_df, input_col="cleaned_text", output_col="words")
    processed_df = preprocessor.remove_stop_words(processed_df, input_col="words", output_col="filtered_words")
    processed_df = preprocessor.hashing_tf.transform(processed_df)
    processed_df = preprocessor.idf_model.transform(processed_df)
    
    # Make predictions
    predictions = model.transform(processed_df)
    
    return predictions


def display_predictions(predictions):
    """
    Display predictions in a readable format
    
    Args:
        predictions (DataFrame): Predictions DataFrame
    """
    print("\n" + "=" * 80)
    print("PREDICTIONS")
    print("=" * 80)
    
    results = predictions.select("message", "prediction", "probability").collect()
    
    for i, row in enumerate(results, 1):
        message = row['message']
        prediction = int(row['prediction'])
        probability = row['probability']
        
        label = "TOXIC" if prediction == 1 else "NON-TOXIC"
        confidence = probability[prediction] * 100
        
        print(f"\n[{i}] Message: {message}")
        print(f"    Prediction: {label}")
        print(f"    Confidence: {confidence:.2f}%")
        print(f"    Probabilities: [Non-toxic: {probability[0]:.4f}, Toxic: {probability[1]:.4f}]")
    
    print("\n" + "=" * 80)


def predict_from_file(spark, model, file_path, preprocessor):
    """
    Predict toxicity for messages in a CSV file
    
    Args:
        spark (SparkSession): Spark session
        model: Trained model
        file_path (str): Path to CSV file with messages
        preprocessor (TextPreprocessor): Initialized preprocessor with IDF model
        
    Returns:
        DataFrame: Predictions DataFrame
    """
    # Load messages from file
    messages_df = spark.read.csv(file_path, header=True, inferSchema=True)
    
    # Preprocess messages using the loaded preprocessor
    processed_df = preprocessor.preprocess_dataframe(messages_df, text_column="message")
    processed_df = preprocessor.tokenize_text(processed_df, input_col="cleaned_text", output_col="words")
    processed_df = preprocessor.remove_stop_words(processed_df, input_col="words", output_col="filtered_words")
    processed_df = preprocessor.hashing_tf.transform(processed_df)
    processed_df = preprocessor.idf_model.transform(processed_df)
    
    # Make predictions
    predictions = model.transform(processed_df)
    
    return predictions


def main():
    """Main prediction function"""
    parser = argparse.ArgumentParser(description="Predict Message Toxicity")
    parser.add_argument("--model-path", type=str, default="models/toxicity_model",
                        help="Path to the trained model")
    parser.add_argument("--model-type", type=str, default="logistic_regression",
                        choices=["logistic_regression", "random_forest"],
                        help="Type of model")
    parser.add_argument("--num-features", type=int, default=1000,
                        help="Number of TF-IDF features")
    parser.add_argument("--message", type=str, nargs="*",
                        help="Message(s) to predict")
    parser.add_argument("--file", type=str,
                        help="CSV file with messages to predict")
    parser.add_argument("--output", type=str,
                        help="Path to save predictions CSV")
    
    args = parser.parse_args()
    
    # Create Spark session
    print("=== Initializing Spark Session ===")
    spark = create_spark_session()
    
    try:
        # Load model
        print("=== Loading Model ===")
        model = load_model(args.model_path, args.model_type)
        
        # Load preprocessor with IDF model
        print("=== Loading Preprocessor ===")
        idf_model_path = args.model_path + "_idf"
        preprocessor = load_preprocessor(idf_model_path, args.num_features)
        
        # Make predictions
        if args.message:
            # Predict from command line messages
            predictions = predict_messages(spark, model, args.message, preprocessor)
            display_predictions(predictions)
        
        elif args.file:
            # Predict from file
            print(f"\n=== Predicting from file: {args.file} ===")
            predictions = predict_from_file(spark, model, args.file, preprocessor)
            display_predictions(predictions)
            
            # Save predictions if output path provided
            if args.output:
                predictions.select("message", "prediction", "probability").coalesce(1).write.csv(
                    args.output, header=True, mode="overwrite"
                )
                print(f"\nPredictions saved to {args.output}")
        
        else:
            # Interactive mode with example messages
            print("\n=== Running with Example Messages ===")
            example_messages = [
                "You are amazing! Keep up the great work!",
                "I hate you and hope you fail",
                "Thank you for your help today",
                "Shut up you stupid idiot",
                "Great job on the presentation!",
                "You're worthless and nobody likes you"
            ]
            
            predictions = predict_messages(spark, model, example_messages, preprocessor)
            display_predictions(predictions)
    
    finally:
        # Stop Spark session
        spark.stop()


if __name__ == "__main__":
    main()
