"""
Example Usage Script
Demonstrates how to use the toxicity detection system
"""

from pyspark.sql import SparkSession
from src.preprocessing import TextPreprocessor
from src.model import ToxicityClassifier


def example_basic_usage():
    """
    Basic example: Train and predict with simple workflow
    """
    print("=" * 80)
    print("BASIC USAGE EXAMPLE")
    print("=" * 80)
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("ToxicityDetectorExample") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        # Load data
        print("\n1. Loading data...")
        train_df = spark.read.csv("data/train_data.csv", header=True, inferSchema=True)
        print(f"   Loaded {train_df.count()} training samples")
        
        # Preprocess data
        print("\n2. Preprocessing data...")
        preprocessor = TextPreprocessor()
        train_processed = preprocessor.full_pipeline(train_df, text_column="message")
        print("   Preprocessing completed")
        
        # Train model
        print("\n3. Training model...")
        classifier = ToxicityClassifier(model_type="logistic_regression")
        classifier.create_model(max_iter=50)
        classifier.train(train_processed)
        print("   Model trained successfully")
        
        # Create test messages
        print("\n4. Making predictions...")
        test_messages = [
            ("Thank you for your help!",),
            ("You are stupid and worthless",),
            ("Great job on the project!",),
            ("I hate everything about you",)
        ]
        
        test_df = spark.createDataFrame(test_messages, ["message"])
        test_processed = preprocessor.preprocess_dataframe(test_df, "message")
        test_processed = preprocessor.tokenize_text(test_processed)
        test_processed = preprocessor.remove_stop_words(test_processed)
        test_processed = preprocessor.hashing_tf.transform(test_processed)
        test_processed = preprocessor.idf_model.transform(test_processed)
        
        predictions = classifier.predict(test_processed)
        
        print("\n   Predictions:")
        for row in predictions.select("message", "prediction").collect():
            label = "TOXIC" if row.prediction == 1.0 else "NON-TOXIC"
            print(f"   - '{row.message}' -> {label}")
        
        print("\n✓ Example completed successfully!")
        
    finally:
        spark.stop()


def example_with_custom_preprocessing():
    """
    Example with custom preprocessing steps
    """
    print("\n" + "=" * 80)
    print("CUSTOM PREPROCESSING EXAMPLE")
    print("=" * 80)
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("CustomPreprocessingExample") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        # Load sample data
        print("\n1. Creating sample data...")
        sample_data = [
            ("Hello! How are you doing today? 😊", 0),
            ("You're such an IDIOT!!! Go away!!!", 1),
            ("Check out this link: http://example.com", 0),
            ("I HATE YOU SO MUCH!!!!", 1),
        ]
        
        df = spark.createDataFrame(sample_data, ["message", "label"])
        
        # Show original messages
        print("\n2. Original messages:")
        for row in df.collect():
            print(f"   - {row.message}")
        
        # Apply preprocessing
        print("\n3. Applying preprocessing...")
        preprocessor = TextPreprocessor()
        
        # Clean text
        df_cleaned = preprocessor.preprocess_dataframe(df, "message")
        
        print("\n4. Cleaned messages:")
        for row in df_cleaned.select("message", "cleaned_text").collect():
            print(f"   Original: {row.message}")
            print(f"   Cleaned:  {row.cleaned_text}")
            print()
        
        # Tokenize
        df_tokenized = preprocessor.tokenize_text(df_cleaned)
        
        print("5. Tokenized samples:")
        for row in df_tokenized.select("cleaned_text", "words").collect()[:2]:
            print(f"   Text: {row.cleaned_text}")
            print(f"   Tokens: {row.words}")
            print()
        
        # Remove stop words
        df_filtered = preprocessor.remove_stop_words(df_tokenized)
        
        print("6. After stop word removal:")
        for row in df_filtered.select("words", "filtered_words").collect()[:2]:
            print(f"   Before: {row.words}")
            print(f"   After:  {row.filtered_words}")
            print()
        
        print("✓ Preprocessing demonstration completed!")
        
    finally:
        spark.stop()


def example_model_comparison():
    """
    Example comparing different model types
    """
    print("\n" + "=" * 80)
    print("MODEL COMPARISON EXAMPLE")
    print("=" * 80)
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("ModelComparisonExample") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        # Load and preprocess data
        print("\n1. Loading and preprocessing data...")
        train_df = spark.read.csv("data/train_data.csv", header=True, inferSchema=True)
        test_df = spark.read.csv("data/test_data.csv", header=True, inferSchema=True)
        
        preprocessor = TextPreprocessor()
        train_processed = preprocessor.full_pipeline(train_df, text_column="message", num_features=500)
        
        test_processed = preprocessor.preprocess_dataframe(test_df, "message")
        test_processed = preprocessor.tokenize_text(test_processed)
        test_processed = preprocessor.remove_stop_words(test_processed)
        test_processed = preprocessor.hashing_tf.transform(test_processed)
        test_processed = preprocessor.idf_model.transform(test_processed)
        
        # Compare models
        models = [
            ("Logistic Regression", "logistic_regression", {"max_iter": 50}),
            ("Random Forest", "random_forest", {"num_trees": 10, "max_depth": 5})
        ]
        
        results = []
        
        for model_name, model_type, params in models:
            print(f"\n2. Training {model_name}...")
            classifier = ToxicityClassifier(model_type=model_type)
            classifier.create_model(**params)
            classifier.train(train_processed)
            
            predictions = classifier.predict(test_processed)
            metrics = classifier.evaluate(predictions)
            
            results.append((model_name, metrics))
        
        # Display comparison
        print("\n3. Model Performance Comparison:")
        print("-" * 80)
        print(f"{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
        print("-" * 80)
        
        for model_name, metrics in results:
            print(f"{model_name:<25} "
                  f"{metrics['accuracy']:<12.4f} "
                  f"{metrics['precision']:<12.4f} "
                  f"{metrics['recall']:<12.4f} "
                  f"{metrics['f1_score']:<12.4f}")
        
        print("-" * 80)
        print("\n✓ Model comparison completed!")
        
    finally:
        spark.stop()


if __name__ == "__main__":
    """Run all examples"""
    
    print("\n")
    print("*" * 80)
    print("CHAT MESSAGE TOXICITY DETECTOR - USAGE EXAMPLES")
    print("*" * 80)
    
    # Run examples
    try:
        example_basic_usage()
        example_with_custom_preprocessing()
        example_model_comparison()
        
        print("\n" + "*" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("*" * 80)
        print("\nNext steps:")
        print("  1. Run 'python train.py' to train a model")
        print("  2. Run 'python predict.py' to make predictions")
        print("  3. Check the README.md for more detailed usage instructions")
        print("*" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("Please ensure:")
        print("  - PySpark is installed: pip install pyspark")
        print("  - Data files exist in the data/ directory")
        print("  - Java 8+ is installed and JAVA_HOME is set")
