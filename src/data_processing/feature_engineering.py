import pandas as pd
from sklearn.model_selection import train_test_split
from pandas import DataFrame, Series
from typing import Tuple, Dict, Any
from loguru import logger

class FeatureEngineer:
    """
    Worker: Handles Data Representation and Feature Engineering.
    Responsibilities: Extraction, Encoding, and X/y Splitting.
    """
    def __init__(self, rules: dict, target_column: str, split_config: dict):
        # Config-Driven Architecture: All logic parameters are externalized
        self.rules = rules
        self.target_column = target_column
        self.split_config = split_config

        logger.info("FeatureEngineer initialized.")

    def transform_and_split(self, df: pd.DataFrame) -> Tuple[DataFrame, Series, DataFrame, Series, Dict[str, str]]:
        """
        Performs feature engineering and returns five distinct artifacts.
        """
        # Immutability: Ensure the original dataframe is not modified in-place
        df = df.copy()
        logger.info("Starting feature engineering (Representation) phase...")

        # Generic Custom Extractions
        # Replace specific 'Cabin' logic with a loop over config-defined extractions
        custom_extractions = self.rules.get("custom_extractions", [])
        for ext_cfg in custom_extractions:
            col_name = ext_cfg.get("column")
            if col_name in df.columns:
                logger.debug(f"Applying custom extraction on {col_name}...")
                # Example: regex extraction based on config
                df[ext_cfg.get("new_col")] = df[col_name].str.extract(ext_cfg.get("regex"))[0]
                df[ext_cfg.get("new_col")] = df[ext_cfg.get("new_col")].fillna(ext_cfg.get("default", "U"))
                df = df.drop(columns=[col_name])

        # Encoding Logic
        encode_rules = self.rules.get("encoding_rules", {})
        for col, mapping in encode_rules.items():
            if col in df.columns:
                df[col] = df[col].map(mapping)
                logger.debug(f"Encoded {col} using mapping.")

        # Target Validation (Fail-Fast Pattern)
        if self.target_column not in df.columns:
            logger.error(f"Target column '{self.target_column}' not found.")
            raise ValueError(f"Target column '{self.target_column}' not found in DataFrame.")

        # Separate features and target
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]

        # The Split: Parameters pulled from config
        X_train, X_test, y_train, y_test = train_test_split(
            X, 
            y, 
            test_size=self.split_config["test_size"],
            random_state=self.split_config["random_state"],
            stratify=y 
        )
        
        logger.info(f"Data split complete. Train size: {len(X_train)}, Test size: {len(X_test)}")

        # Dynamic Schema Generation for Contract Validation
        dynamic_schema: Dict[str, str] = {
            str(col): str(dtype) for col, dtype in X_train.dtypes.items()
        }

        return X_train, y_train, X_test, y_test, dynamic_schema
