import sys
from pathlib import Path
from dataclasses import asdict
from loguru import logger

# --- Framework Imports ---
from src.config.config_loader import config
from src.data_processing.data_loader import DataLoader
from src.data_processing.preprocessing import DataPreprocessor
from src.data_processing.feature_engineering import FeatureEngineer
from src.data_processing.validator import DataValidator
from src.utils.persistence import ArtifactManager
from src.evaluation.evaluator import ModelEvaluator
from src.utils.logger import setup_logger 

# --- Model Worker Imports ---
from src.model.sklearn_worker import SklearnRandomForestWorker
# In a scaling system, you would import multiple workers here:
# from src.model.xgboost_worker import XgboostWorker

class ModelFactory:
    """
    Factory Pattern: Decouples the Orchestrator from specific Model implementations.
    The Orchestrator asks for a model by 'type', and the Factory handles instantiation.
    """
    @staticmethod
    def get_worker(model_cfg) -> Any:
        # This logic allows swapping models via config.yaml without touching train.py
        if model_cfg.type == "random_forest":
            return SklearnRandomForestWorker(model_cfg)
        # Add other models here (e.g., "xgboost", "svm")
        else:
            raise ValueError(f"Model type '{model_cfg.type}' is not supported by the Factory.")


def main():
    try:
        # Initialize Structured Logging
        setup_logger(asdict(config.logging))
        logger.info("Configuration loaded successfully.")
    
        # --- CONFIGURATION SLICING (Separation of Concerns) ---
        # Extracting slices ensures the Orchestrator only holds the data it needs.
        data_cfg = config.data
        artifacts_cfg = config.artifacts
        model_cfg = config.model
        pre_cfg = config.data.preprocessing
        source_schema = config.data.schema
    
        # --- PHASE 1: DATA ENGINEERING ---
        # State Transition: Raw Data -> Sanitized Data -> Feature Matrix
        logger.info("--- Starting Pipeline: Data Engineering Phase ---")
            
        # 1.1 Load Raw Data (I/O Worker)
        loader = DataLoader(config.paths)
        raw_data = loader.load_csv(artifacts_cfg.input_file)
        
        # 1.2 Contract Validation (Ingress Gate)
        # Fail-Fast: Ensure data integrity before any transformations occur.
        validator_raw = DataValidator(source_schema)
        validator_raw.validate(raw_data)
    
        # 1.3 Data Sanitization (Sanitization Worker)
        # Uses Config-Driven rules for dropping columns and imputation.
        processed_path_obj = Path(config.paths.processed_data) 
        preprocessor = DataPreprocessor(
            rules=pre_cfg, 
            processed_path=processed_path_obj
        )
        sanitized_data = preprocessor.clean_data(raw_data)
        
        # 1.4 Intermediate Persistence (Persistence Engine)
        # Save state for auditability and reproducibility.
        preprocessor.save_processed_data(
            sanitized_data, 
            filename=artifacts_cfg.output_file
        )
    
        # 1.5 Feature Engineering & Splitting (Representation Worker)
        engineer = FeatureEngineer(
            rules=pre_cfg, 
            target_column=data_cfg.target_column, 
            split_config=data_cfg.split_config
        )
        
        # Dynamic Schema Generation: Capture the result of the transformation
        X_train, y_train, X_test, y_test, dynamic_schema = engineer.transform_and_split(sanitized_data)
    
        # 1.6 Contract Validation (Egress Gate)
        # Validate the feature matrix against the dynamically generated schema.
        logger.info("--- Starting Contract Validation Phase - post-engineering ---")
        validator_final = DataValidator(dynamic_schema)
        validator_final.validate(X_train) 
    
        # --- PHASE 2: MODEL ENGINEERING ---
        # State Transition: Feature Matrix -> Trained Model Weights
        logger.info("--- Starting Model Engineering Phase ---")
        
        # Initialize Persistence Engine
        artifact_manager = ArtifactManager(Path(config.paths.models))
        
        # Initialize Model Worker via Factory (Abstraction Layer)
        # The Orchestrator is now agnostic to the specific Sklearn implementation.
        worker = ModelFactory.get_worker(model_cfg)
        
        # Execute Training and save weights
        worker.train(X_train, y_train)
        model_path = worker.save(artifact_manager)
    
        # --- PHASE 3: EVALUATION & OBSERVABILITY ---
        # State Transition: Model Weights + Test Data -> Metrics Artifacts
        logger.info("--- Starting Evaluation Phase ---")
        metrics = ModelEvaluator.evaluate(worker, X_test, y_test)
        
        # Persistence of metadata (Metrics, Hyperparams, Model URI)
        artifact_manager.save_metrics(
            metrics=metrics, 
            model_name=config.model.name, 
            model_uri=str(model_path),
            hyperparameters=config.model.params,
            training_params=config.training
        )
    
        logger.success("Pipeline executed successfully.")
        
    except RuntimeError as e:
        # Catch specific Domain/Validation errors (e.g., Schema Mismatch)
        logger.error(f"Validation Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        # Catch System-level failures (e.g., Out of Memory, Disk Full)
        logger.critical(f"Unexpected System Failure: {str(e)}")
        logger.exception("Stack trace for debugging:")
        sys.exit(1)

if __name__ == "__main__":
    main()
