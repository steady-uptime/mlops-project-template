from loguru import logger
import pandas as pd
from typing import Dict, List, Union

class DataValidator:
    """
    Gatekeeper for Contract Validation.
    Ensures that the processed DataFrame matches the expected schema.
    Follows a Fail-Fast pattern.
    """
    TYPE_MAPPINGS = {
        "object": ["object", "str"],
        "str": ["object", "str"],
        "float": ["float64", "float32", "float"],
        "int": ["int64", "int32", "int"]
    }
    
    def __init__(self, expected_schema: Union[Dict[str, str], List[Dict[str, str]]]):
        """
        Accepts a schema contract.
        """
        if isinstance(expected_schema, list):
            logger.debug("Converting list-based schema to dictionary format.")
            self.expected_schema = {item['column']: item['type'] for item in expected_schema}
        else:
            self.expected_schema = expected_schema

    def validate(self, df: pd.DataFrame) -> None:
        """
        Validates the DataFrame against the provided schema.
        Raises RuntimeError if the contract is violated.
        """
        logger.info("Starting contract validation...")
        
        # Check for missing columns
        missing_cols = set(self.expected_schema.keys()) - set(df.columns)
        if missing_cols:
            logger.error(f"DataFrame Head at point of failure:\n{df.head()}")
            error_msg = f"Contract Validation Failed: Missing columns: {missing_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Check for type mismatches
        for col, expected_type in self.expected_schema.items():
            if col not in df.columns:
                continue
            
            actual_type = str(df[col].dtype)
            is_valid = False
            
            if expected_type in self.TYPE_MAPPINGS and actual_type in self.TYPE_MAPPINGS[expected_type]:
                is_valid = True
            elif actual_type in self.TYPE_MAPPINGS and expected_type in self.TYPE_MAPPINGS[actual_type]:
                is_valid = True
            elif expected_type in actual_type:
                is_valid = True

            if not is_valid:
                logger.error(f"DataFrame Head at point of failure:\n{df.head()}")
                error_msg = f"Contract Validation Failed: Column '{col}' expected {expected_type}, got {actual_type}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        logger.success("Contract validation passed.")
