import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Configure logging for the boot sequence
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigLoader:
    # Type Hint: This will hold the Singleton instance
    _instance: Optional["ConfigLoader"] = None
    
    # Type Hint: This holds the configuration dictionary
    _config: Optional[Dict[str, Any]] = None

    # Type Hint: This holds the absolute path to the project root
    project_root: Optional[Path] = None

    def __new__(cls) -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._initialize_config()
        return cls._instance

    @classmethod
    def _initialize_config(cls) -> None:
        """
        Internal method to handle I/O and configuration injection.
        Separates the 'Boot Logic' from the 'Instance Lifecycle'.
        """
        # Law #1 & #3: Dynamically calculate project root
        # Path(__file__).resolve() is the standard for Portability.
        cls.project_root = Path(__file__).resolve().parent.parent.parent
        
        config_path = cls.project_root / "configs" / "config.yaml"
        
        logger.info(f"System: Initializing configuration from {config_path}")

        if not config_path.exists():
            logger.error(f"Configuration file not found at {config_path}")
            raise FileNotFoundError(f"Config file missing: {config_path}")

        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
            
            # State Synchronization: Inject the project_root into the dictionary
            # This ensures the config object is the Single Source of Truth.
            config_data["project_root"] = str(cls.project_root)
            cls._config = config_data
            
            logger.info("System: Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"System: Failed to load configuration: {e}")
            raise

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Returns the loaded configuration dictionary.
        Uses Type Narrowing to satisfy static analysis.
        """
        if cls._config is None:
            # Force initialization if accessed before __new__ is triggered
            ConfigLoader() 
        
        # Type Guard: Assert that the config is no longer None.
        # This tells Pylance: "If the code reaches this line, _config is guaranteed to be a Dict."
        assert cls._config is not None, "Configuration failed to load."
        
        return cls._config

# Global instance for easy importing across the Software Stack.
# This provides a clean, decoupled interface for other modules.
config = ConfigLoader().get_config()
