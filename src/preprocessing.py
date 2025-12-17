"""
Data Preprocessing Module
Handles text cleaning, tokenization, and feature extraction
"""

import re
from pyspark.sql import DataFrame
from pyspark.sql.functions import udf, col, lower, regexp_replace
from pyspark.sql.types import StringType, ArrayType
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF


class TextPreprocessor:
    """
    Handles text preprocessing for toxicity detection
    """
    
    def __init__(self):
        """Initialize the preprocessor"""
        self.tokenizer = None
        self.stop_words_remover = None
        self.hashing_tf = None
        self.idf_model = None
        # Create UDF once at initialization for better performance
        self._clean_text_udf = udf(self.clean_text, StringType())
    
    @staticmethod
    def clean_text(text):
        """
        Clean text by removing special characters and extra spaces
        
        Args:
            text (str): Input text to clean
            
        Returns:
            str: Cleaned text
        """
        if text is None:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and numbers, keep only letters and spaces
        text = re.sub(r'[^a-z\s]', '', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def preprocess_dataframe(self, df: DataFrame, text_column="message") -> DataFrame:
        """
        Preprocess the dataframe by cleaning text
        
        Args:
            df (DataFrame): Input PySpark DataFrame
            text_column (str): Name of the text column
            
        Returns:
            DataFrame: Preprocessed DataFrame
        """
        # Apply text cleaning using the pre-created UDF
        df = df.withColumn("cleaned_text", self._clean_text_udf(col(text_column)))
        
        return df
    
    def tokenize_text(self, df: DataFrame, input_col="cleaned_text", output_col="words") -> DataFrame:
        """
        Tokenize text into words
        
        Args:
            df (DataFrame): Input DataFrame
            input_col (str): Column containing text
            output_col (str): Column for tokenized output
            
        Returns:
            DataFrame: DataFrame with tokenized text
        """
        self.tokenizer = Tokenizer(inputCol=input_col, outputCol=output_col)
        df = self.tokenizer.transform(df)
        return df
    
    def remove_stop_words(self, df: DataFrame, input_col="words", output_col="filtered_words") -> DataFrame:
        """
        Remove stop words from tokenized text
        
        Args:
            df (DataFrame): Input DataFrame
            input_col (str): Column containing tokenized words
            output_col (str): Column for filtered output
            
        Returns:
            DataFrame: DataFrame with stop words removed
        """
        self.stop_words_remover = StopWordsRemover(inputCol=input_col, outputCol=output_col)
        df = self.stop_words_remover.transform(df)
        return df
    
    def extract_tfidf_features(self, df: DataFrame, input_col="filtered_words", 
                                raw_features_col="raw_features", features_col="features",
                                num_features=1000) -> DataFrame:
        """
        Extract TF-IDF features from text
        
        Args:
            df (DataFrame): Input DataFrame
            input_col (str): Column containing filtered words
            raw_features_col (str): Column for raw TF features
            features_col (str): Column for TF-IDF features
            num_features (int): Number of features for hashing
            
        Returns:
            DataFrame: DataFrame with TF-IDF features
        """
        # Apply HashingTF
        self.hashing_tf = HashingTF(inputCol=input_col, outputCol=raw_features_col, numFeatures=num_features)
        df = self.hashing_tf.transform(df)
        
        # Apply IDF
        idf = IDF(inputCol=raw_features_col, outputCol=features_col)
        self.idf_model = idf.fit(df)
        df = self.idf_model.transform(df)
        
        return df
    
    def full_pipeline(self, df: DataFrame, text_column="message", num_features=1000) -> DataFrame:
        """
        Run the full preprocessing pipeline
        
        Args:
            df (DataFrame): Input DataFrame
            text_column (str): Name of the text column
            num_features (int): Number of features for TF-IDF
            
        Returns:
            DataFrame: Fully preprocessed DataFrame with features
        """
        # Clean text
        df = self.preprocess_dataframe(df, text_column)
        
        # Tokenize
        df = self.tokenize_text(df, input_col="cleaned_text", output_col="words")
        
        # Remove stop words
        df = self.remove_stop_words(df, input_col="words", output_col="filtered_words")
        
        # Extract TF-IDF features
        df = self.extract_tfidf_features(df, input_col="filtered_words", num_features=num_features)
        
        return df
    
    def save_idf_model(self, path: str) -> None:
        """
        Save the IDF model
        
        Args:
            path (str): Path to save the IDF model
        """
        if self.idf_model is None:
            raise ValueError("No IDF model to save. Train the model first.")
        
        self.idf_model.write().overwrite().save(path)
        print(f"IDF model saved to {path}")
    
    def load_idf_model(self, path: str) -> None:
        """
        Load the IDF model
        
        Args:
            path (str): Path to load the IDF model from
        """
        from pyspark.ml.feature import IDFModel
        self.idf_model = IDFModel.load(path)
        print(f"IDF model loaded from {path}")
