import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

# --- Configuration Schema (The Contracts) ---
# Using Dataclasses ensures Type Safety and provides a schema for the configuration.

@dataclass(frozen=True)
class EnvConfig:
    mode: str
    compute: Dict[str, Any]

@dataclass(frozen=True)
class DataConfig:
    target_column: str
    split_config: Dict[str, Any]
    preprocessing: Dict[str, Any]
    schema: list

    def validate(self):
        """Contract Validation for Data Engineering parameters."""
        if not self.target_column:
            raise ValueError("DataConfig: target_column must not be empty.")

@dataclass(frozen=True)
class ModelConfig:
    name: str
    type: str
    params: Dict[str, Any]

@dataclass(frozen=True)
class TrainingConfig:
    learning_rate: float
    batch_size: int
    epochs: int

    def validate(self):
        """Contract Validation for Training Hyperparameters."""
        if not (0 < self.learning_rate < 1):
            raise ValueError(f"TrainingConfig: Invalid learning_rate ({self.learning_rate}). Must be between 0 and 1.")
        if self.batch_size <= 0:
            raise ValueError(f"TrainingConfig: Invalid batch_size ({self.batch_size}). Must be > 0.")
        if self.epochs <= 0:
            raise ValueError(f"TrainingConfig: Invalid epochs ({self.epochs}). Must be > 0.")
        
@dataclass(frozen=True)
class PathsConfig:
    external_data: str
    logs: str
    models: str
    processed_data: str
    raw_data: str

@dataclass(frozen=True)
class ArtifactConfig:
    input_file: str
    output_file: str
    base_path: str

@dataclass(frozen=True)
class LoggingConfig:
    file_path: str
    level: str
    rotation: str
    retention: str

@dataclass(frozen=True)
class AppConfig:
    project_name: str
    env: EnvConfig
    data: DataConfig
    paths: PathsConfig
    model: ModelConfig
    training: TrainingConfig
    artifacts: ArtifactConfig
    logging: LoggingConfig
    project_root: str

    def validate(self):
        """Aggregate validation for all sub-configs."""
        self.data.validate()
        self.training.validate()


# --- Singleton Loader ---

class ConfigLoader:
    """
    Singleton class to load and validate the project configuration.
    Ensures the project root is calculated once and shared globally.
    """
    _instance: Optional["ConfigLoader"] = None
    _config: Optional[AppConfig] = None
    project_root: Optional[Path] = None

    def __new__(cls) -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._initialize_config()
        return cls._instance

    @classmethod
    def _initialize_config(cls) -> None:
        # Law #1 & #3: Dynamically calculate project root for Portability.
        # This allows the project to run on any OS/Directory without absolute paths.
        if cls.project_root is None:
            cls.project_root = Path(__file__).resolve().parent.parent.parent
        
        config_path = cls.project_root / "configs" / "config.yaml"
        
        logger.info(f"System: Loading configuration from {config_path}")

        if not config_path.exists():
            logger.error(f"Configuration file missing: {config_path}")
            raise FileNotFoundError(f"Config file missing: {config_path}")

        try:
            with open(config_path, "r") as f:
                raw_data = yaml.safe_load(f)
            
            # Inject the project_root into the raw data for use in paths
            raw_data["project_root"] = str(cls.project_root)

            # Apply environment variable overrides (Configuration Precedence)
            raw_data = cls._apply_env_overrides(raw_data)

            # Mapping raw YAML to Dataclasses for type safety and dot-notation access
            cls._config = AppConfig(
                project_name=raw_data["project_name"],
                env=EnvConfig(**raw_data["env"]),
                data=DataConfig(**raw_data["data"]),
                paths=PathsConfig(**raw_data["paths"]),
                model=ModelConfig(**raw_data["model"]),
                training=TrainingConfig(**raw_data["training"]),
                artifacts=ArtifactConfig(**raw_data["artifacts"]),
                logging=LoggingConfig(**raw_data["logging"]),
                project_root=raw_data["project_root"]
            )
            
            # Contract Validation Gate
            cls._config.validate()
            
            logger.info("System: Configuration successfully loaded, mapped, and validated.")
        except Exception as e:
            logger.error(f"System: Configuration Initialization Failed: {e}")
            raise

    @staticmethod
    def _apply_env_overrides(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements Configuration Precedence.
        Allows environment variables to override YAML values. This is crucial for 
        DevOps/SRE workflows, allowing the same container image to be reused 
        across different environments by changing the ConfigMap/Secrets.
        """
        env_mapping = raw_data.get("env_mapping", {})

        for env_var, mapping_values in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # mapping_values is a list from YAML, e.g., ["paths", "raw_data"]
                section, key = mapping_values 
                
                if section in raw_data and key in raw_data[section]:
                    target_type = type(raw_data[section][key])
                    
                    # Type casting logic to ensure Environment Variables (strings) 
                    # match the required Dataclass types.
                    if target_type == bool:
                        overridden_value = env_value.lower() in ("true", "1", "yes")
                    elif target_type in (int, float):
                        overridden_value = target_type(env_value)
                    else:
                        overridden_value = env_value
                    
                    raw_data[section][key] = overridden_value
                    logger.info(f"System: Overriding {section}.{key} with EnvVar {env_var}")

        return raw_data

    @classmethod
    def get_config(cls) -> AppConfig:
        if cls._config is None:
            ConfigLoader() 
        assert cls._config is not None, "Configuration failed to load."
        return cls._config

# Global instance for the Software Stack.
# This provides the Single Source of Truth for the entire project.
config = ConfigLoader().get_config()
