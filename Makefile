.PHONY: install run train evaluate predict test

# Install dependencies
# This remains a shell command as it interacts with the system package manager/pip
install:
	pip install -r requirements.txt

# Orchestrate the full pipeline
# Executes the main pipeline module
run:
	python -m scripts.run_pipeline

# Model Engineering: Training
# Executes the training module
train:
	python -m scripts.train

# Model Engineering: Evaluation
# Executes the evaluation module
evaluate:
	python -m scripts.evaluate

# Model Engineering: Inference
# Executes the prediction module
predict:
	python -m scripts.predict

# Quality Assurance: Unit & Integration Tests
# pytest is called as a binary tool
test:
	pytest -q
    