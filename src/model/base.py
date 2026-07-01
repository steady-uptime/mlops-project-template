from typing import Any, TypeVar, Generic, Optional
from src.config.config_loader import ModelConfig
from abc import ABC, abstractmethod
import pandas as pd

# TypeVar for better type inference in subclasses
T = TypeVar('T')

class ModelWorker(ABC, Generic[T]):
    """
    Abstract Base Class for all model workers.
    Enforces a consistent interface for Training and Inference.
    """
    def __init__(self, config: ModelConfig):
        self.config = config
        # Generic placeholder for the specific model instance
        self.model: Optional[T] = None

    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def save(self, persistence_engine: Any) -> None:
        pass

    @abstractmethod
    def load(self, persistence_engine: Any) -> None:
        pass
