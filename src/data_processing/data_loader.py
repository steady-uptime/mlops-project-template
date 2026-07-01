from src.config.config_loader import PathsConfig
import pandas as pd
from pathlib import Path
from loguru import logger

class DataLoader:
    """
    Worker: Fetches raw data.
    Decoupled: Receives ONLY the paths portion of the config via Dependency Injection.
    """
    def __init__(self, paths_cfg: PathsConfig):
        # Config-Driven Architecture: Paths are resolved via the Singleton Config Loader
        self.raw_path = Path(paths_cfg.raw_data)
        self.processed_path = Path(paths_cfg.processed_data)
        self.external_path = Path(paths_cfg.external_data)
        
        logger.info(f"Initialized DataLoader. Raw data directory: {self.raw_path}")

    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Loads a CSV file from the RAW data path.
        :param filename: The name of the file (e.g., 'dataset.csv')
        :return: Loaded pandas DataFrame
        """
        # Portability First: Pathlib handles cross-platform path joining
        file_path = self.raw_path / filename
        
        logger.info(f"Attempting to load data from: {file_path}")
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"The file {filename} was not found in {self.raw_path}")

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {filename}. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"An error occurred while loading the CSV: {e}")
            raise e
