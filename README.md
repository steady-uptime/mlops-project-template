
# MLOps Framework Template: Production-Grade Architecture

This repository provides a modular, production-ready MLOps framework designed for scalability, portability, and maintainability. It follows strict Software Engineering principles to ensure a seamless transition from model development to production deployment. 

**Note:** This is a generic framework. To use this for a specific project, follow the [Template Adaptation Guide](#template-adaptation-guide) below.

## 🏗 Architecture Principles

To ensure production readiness, this framework adheres to the following engineering constraints:

- **Config-Driven Architecture**: Zero hardcoding. All hyperparameters, file paths, and transformation rules are externalized in `configs/`.
- **Decoupled Logic**: Strict Separation of Concerns (SoC) between Data Engineering (ETL), Model Engineering (Training/Inference), and Orchestration (Workflow Management).
- **Portability**: All paths are resolved dynamically via a Singleton Configuration Loader using `pathlib`, ensuring the project runs on any OS (Windows, Linux, macOS) without modification.
- **Artifact Immutability**: Data transformations and model saves produce new artifacts rather than modifying source data or state in place.

## 🚀Project Status & Lifecycle

This framework is organized into five distinct engineering phases:

- [ ] **Phase 1: Configuration Engine** (Singleton Config Loader, Environment Profile Support)
- [ ] **Phase 2: Data Engineering Pipeline** (Worker-based ETL, Dynamic Preprocessing)
- [ ] **Phase 3: Model Engineering** (Trainable Workers, Artifact Management)
- [ ] **Phase 4: Evaluation & Orchestration** (Metrics, Structured Logging, Scheduling)
- [ ] **Phase 5: Deployment** (Docker, Kubernetes, API Gateway)

## 🧩Component Breakdown

### 1. Configuration Management (`configs/`)
- **Singleton Pattern**: The `src/config/config_loader.py` ensures that the configuration is loaded into memory once. This provides a **Single Source of Truth** and prevents redundant I/O operations across the application.
- **Profile Support**: Supports `development`, `staging`, and `production` profiles to manage different environment behaviors (e.g., different data paths or logging levels).

### 2. Data Engineering (`src/data_processing/`)
- **Worker Pattern**: Data loading and preprocessing are abstracted into dedicated worker classes.
- **Dynamic Preprocessing**: The pipeline handles data cleaning (imputation, encoding, etc.) via configuration injection rather than hardcoded logic.
- **Dependency Injection**: Preprocessing methods receive specific configuration slices, making the logic easily testable and modular.

### 3. Model Engineering (`src/model/`)
- **Abstract Base Classes (ABC)**: Defines a strict contract for all model workers (e.g., `.fit()`, `.predict()`). This ensures that any model (Scikit-Learn, XGBoost, PyTorch) swapped into the pipeline maintains a consistent interface.
- **Persistence Layer**: Standardized serialization of model artifacts using `joblib` to ensure reproducibility.

### 4. Orchestration (`scripts/`)
- **Manager Pattern**: Orchestrator scripts manage the lifecycle of the data flow, acting as the "Manager" that delegates tasks to specialized "Worker" modules.

## 🛠 Development Setup

### 1. Environment Variables
Set the environment variables to allow the `ConfigLoader` to resolve the project root and active profile.

> [!Windows]
```powershell
$env:PYTHONPATH = "."
$env:CONFIG_PROFILE = "development"
```

> [!Linux/macOS]
```bash
export PYTHONPATH=.
export CONFIG_PROFILE=development
```

### 2. Virtual Environment
```bash
# Create the virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Execution Pipeline
Execute the stages sequentially via the orchestrator scripts:

##### **Data Engineering:**
`python -m scripts.run_preprocessing` 
*(Note: This triggers the Data Engineering Workers)*

##### **Model Training:**
`python -m scripts.train` 
*(Note: This triggers the Model Engineering Workers)*

## 🏗 Infrastructure

- **Docker**: Containerized environment definition in `/docker`.
- **Kubernetes**: Manifests for deployment orchestration in `/k8s`.

## 🧪 Testing & Quality Assurance
- **Unit/Integration Tests**: `pytest tests/`
- **Logging**: Centralized structured logging routed to the `logs/` directory via `loguru`.

---

## 📝 Template Adaptation Guide

To adapt this framework to your specific project (e.g., Titanic, Fraud Detection, Demand Forecasting), modify the following components:

1.  **Configuration**: Update `configs/config.yaml` with your specific hyperparameters, feature lists, and file paths.
2.  **Data Schema**: Update `src/data_processing/validator.py` to define your specific data schema (e.g., expected column names and types).
3.  **Data Workers**: Implement your specific cleaning/engineering logic within `src/data_processing/`.
4.  **Model Workers**: Create a new class in `src/model/` inheriting from `ModelWorker` for your specific algorithm.
5.  **Entry Points**: Update the logic in `scripts/` to call the correct workers for your specific workflow.
