import pandas as pd
import os
from src.config.config_loader import cfg

class DataLoader:
    def __init__(self):
        # Grab the base data path from our settings.yaml
        # This remains portable because cfg.get('data_path') handles the pathing.
        self.data_path = cfg.get('data_path')

    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Generic method to load any CSV file from the configured data path.
        
        Args:
            filename (str): The name of the file (e.g., 'house_prices.csv' or 'churn_data.csv')
            
        Returns:
            pd.DataFrame: The loaded data.
        """
        # Construct the full path dynamically
        full_path = os.path.join(self.data_path, filename)
        
        # Safety check
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Could not find data file at: {full_path}")
            
        print(f"--- Loading data from: {full_path} ---")
        return pd.read_csv(full_path)

# This allows us to test the generic loader independently
if __name__ == "__main__":
    loader = DataLoader()
    # For testing this specific project, we pass the specific filename here
    try:
        data = loader.load_csv("house_prices.csv")
        print("Data Preview:")
        print(data.head())
    except Exception as e:
        print(f"Error: {e}")
