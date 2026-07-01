import json
import joblib
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import is_dataclass, asdict
from datetime import datetime
from loguru import logger

class ArtifactManager:
    """
    Persistence Engine: Handles the 'How' and 'Where' of storage.
    Decoupled from the ML Model logic.
    """
    def __init__(self, base_path: Path):
        # Law 2: Config-Driven. base_path is passed from the config slice.
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ArtifactManager initialized. Base path: {self.base_path}")

    def save_model(self, model: Any, model_name: str) -> Path:
        """
        Serializes the model weights to the filesystem.
        """
        # Logic for filename naming lives here ONLY.
        save_path = self.base_path / f"{model_name}.joblib"
        
        joblib.dump(model, save_path)
        logger.info(f"Model artifact saved to: {save_path}")
        return save_path

    def save_metrics(
        self, 
        metrics: Dict[str, float],
        model_name: str,
        model_uri: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        training_params: Any = None
    ) -> Path:
        """
        Saves evaluation metrics and metadata as a JSON artifact.
        
        Args:
            metrics: Dictionary of performance scores (e.g., Accuracy, F1).
            model_name: Identifier for the model.
            model_uri: Path/Pointer to the serialized weights.
            hyperparameters: Dictionary of training parameters from config.yaml.
            training_params: Optional value, dictionary
        Returns:
            Path: The location of the saved JSON artifact.
        """
        save_path = self.base_path / f"{model_name}_metrics.json"
        
        # Construct the metadata object (The "Contract")
        metadata = {
            "model_name": model_name,
            "metrics": metrics,
            "model_uri": model_uri,  # The pointer to the actual weights
            "hyperparameters": hyperparameters or {},
            "training_params": training_params or {},
            "version_info": "v1.0.0", 
            "timestamp": datetime.now().isoformat(),
            "project_root": str(Path(__file__).resolve().parent.parent.parent) 
        }

        # --- Serialization Gate ---
        # Transform any Dataclasses into dictionaries so the JSON encoder can process them.
        # This ensures the Persistence Layer is robust regardless of what config objects are passed.
        serializable_metadata = {}
        for key, value in metadata.items():
            if is_dataclass(value) and not isinstance(value, type):
                # Convert the Dataclass to a dict
                serializable_metadata[key] = asdict(value)
            elif isinstance(value, dict):
                # Recursively handle dictionaries that might contain nested Dataclasses
                serializable_metadata[key] = {
                    k: (asdict(v) if is_dataclass(v) and not isinstance(v, type) else v)
                    for k, v in value.items()
                }
            else:
                serializable_metadata[key] = value

        try:
            with open(save_path, 'w') as f:
                json.dump(serializable_metadata, f, indent=4)
            logger.info(f"Metrics artifact saved to: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            raise e
            
        return save_path
