"""
Machine Learning Model Module
Handles model training, evaluation, and prediction
"""

from pyspark.ml.classification import (
    LogisticRegression, RandomForestClassifier,
    LogisticRegressionModel, RandomForestClassificationModel
)
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.sql import DataFrame
from typing import Tuple, Dict


class ToxicityClassifier:
    """
    Machine learning classifier for toxicity detection
    """
    
    def __init__(self, model_type="logistic_regression"):
        """
        Initialize the classifier
        
        Args:
            model_type (str): Type of model - 'logistic_regression' or 'random_forest'
        """
        self.model_type = model_type
        self.model = None
        self.trained_model = None
    
    def create_model(self, features_col="features", label_col="label", **kwargs):
        """
        Create the ML model
        
        Args:
            features_col (str): Name of features column
            label_col (str): Name of label column
            **kwargs: Additional parameters for the model
        """
        if self.model_type == "logistic_regression":
            # Logistic Regression model
            max_iter = kwargs.get('max_iter', 100)
            reg_param = kwargs.get('reg_param', 0.01)
            elastic_net_param = kwargs.get('elastic_net_param', 0.0)
            
            self.model = LogisticRegression(
                featuresCol=features_col,
                labelCol=label_col,
                maxIter=max_iter,
                regParam=reg_param,
                elasticNetParam=elastic_net_param
            )
        
        elif self.model_type == "random_forest":
            # Random Forest model
            num_trees = kwargs.get('num_trees', 20)
            max_depth = kwargs.get('max_depth', 5)
            
            self.model = RandomForestClassifier(
                featuresCol=features_col,
                labelCol=label_col,
                numTrees=num_trees,
                maxDepth=max_depth
            )
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, train_df: DataFrame) -> None:
        """
        Train the model
        
        Args:
            train_df (DataFrame): Training DataFrame with features and labels
        """
        if self.model is None:
            self.create_model()
        
        print(f"Training {self.model_type} model...")
        self.trained_model = self.model.fit(train_df)
        print("Model training completed!")
    
    def predict(self, test_df: DataFrame) -> DataFrame:
        """
        Make predictions on test data
        
        Args:
            test_df (DataFrame): Test DataFrame with features
            
        Returns:
            DataFrame: DataFrame with predictions
        """
        if self.trained_model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        predictions = self.trained_model.transform(test_df)
        return predictions
    
    def evaluate(self, predictions_df: DataFrame, label_col="label") -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            predictions_df (DataFrame): DataFrame with predictions and true labels
            label_col (str): Name of the label column
            
        Returns:
            Dict: Dictionary containing evaluation metrics
        """
        # Binary classification evaluator for AUC-ROC
        binary_evaluator = BinaryClassificationEvaluator(
            labelCol=label_col,
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC"
        )
        auc = binary_evaluator.evaluate(predictions_df)
        
        # Multiclass evaluators for accuracy, precision, recall, F1
        multiclass_evaluator = MulticlassClassificationEvaluator(
            labelCol=label_col,
            predictionCol="prediction"
        )
        
        accuracy = multiclass_evaluator.evaluate(predictions_df, {multiclass_evaluator.metricName: "accuracy"})
        precision = multiclass_evaluator.evaluate(predictions_df, {multiclass_evaluator.metricName: "weightedPrecision"})
        recall = multiclass_evaluator.evaluate(predictions_df, {multiclass_evaluator.metricName: "weightedRecall"})
        f1_score = multiclass_evaluator.evaluate(predictions_df, {multiclass_evaluator.metricName: "f1"})
        
        metrics = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "auc_roc": auc
        }
        
        return metrics
    
    def save_model(self, path: str) -> None:
        """
        Save the trained model
        
        Args:
            path (str): Path to save the model
        """
        if self.trained_model is None:
            raise ValueError("No trained model to save")
        
        self.trained_model.write().overwrite().save(path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str, model_class=None) -> None:
        """
        Load a trained model
        
        Args:
            path (str): Path to load the model from
            model_class: Model class to use for loading
        """
        if model_class is None:
            if self.model_type == "logistic_regression":
                model_class = LogisticRegressionModel
            elif self.model_type == "random_forest":
                model_class = RandomForestClassificationModel
        
        self.trained_model = model_class.load(path)
        print(f"Model loaded from {path}")
