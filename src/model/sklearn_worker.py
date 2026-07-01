from src.config.config_loader import ModelConfig
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from src.model.base import ModelWorker
from typing import Any
from loguru import logger

class SklearnRandomForestWorker(ModelWorker):
    def __init__(self, model_cfg: ModelConfig):
        # Parent class accepts the Dataclass slice
        super().__init__(model_cfg)
        
        # Config-Driven: Parameters are unpacked from the config object
        params = self.config.params
        self.model = RandomForestClassifier(**params)
        
        # Explicit State Tracking
        self._is_trained = False 
        logger.info(f"SklearnRandomForestWorker initialized with name: {self.config.name}")

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        logger.info(f"Starting training for {self.config.name}...")
        if self.model is None:
            raise RuntimeError("Model object is not initialized.")
    
        self.model.fit(X, y)
        self._is_trained = True
        logger.success("Training complete.")

    def predict(self, X: pd.DataFrame) -> pd.Series:
        if self.model is None:
            raise RuntimeError("Model object is not initialized.")
        
        if not self._is_trained:
            raise RuntimeError("Cannot perform inference on an untrained model.")
        
        logger.info(f"Performing inference for model: {self.config.name}")
        predictions = self.model.predict(X)
        return pd.Series(predictions)

    def save(self, persistence_engine: Any) -> None:
        """
        The Worker knows the 'What' (the model object and its name).
        The ArtifactManager knows the 'How' (the filesystem path).
        """
        # Contract Validation: Check internal state before allowing persistence
        if not self._is_trained:
            logger.error("Attempted to save an untrained model.")
            raise ValueError("Model must be trained before saving.")

        persistence_engine.save_model(
            model=self.model, 
            model_name=self.config.name
        )

    def load(self, persistence_engine: Any) -> None:
        # Implementation would call persistence_engine.load_model(...)
        pass
