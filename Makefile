# ============================
# Environment
# ============================

.PHONY: install
install:
    pip install -r requirements.txt

.PHONY: format
format:
    black src

.PHONY: lint
lint:
    pylint src

.PHONY: typecheck
typecheck:
    mypy src

# ============================
# Data
# ============================

.PHONY: data
data:
    python src/data/make_dataset.py

# ============================
# Training & Evaluation
# ============================

.PHONY: train
train:
    python src/pipelines/train.py --config configs/training.yaml

.PHONY: evaluate
evaluate:
    python src/pipelines/evaluate.py --config configs/model.yaml

# ============================
# Testing
# ============================

.PHONY: test
test:
    pytest -q

# ============================
# Docker
# ============================

.PHONY: docker-build
docker-build:
    docker build -t project-image -f docker/Dockerfile .

.PHONY: docker-run
docker-run:
    docker run -p 8000:8000 project-image

.PHONY: docker-compose
docker-compose:
    docker-compose -f docker/docker-compose.yaml up

# ============================
# Kubernetes
# ============================

.PHONY: k8s-apply
k8s-apply:
    kubectl apply -f k8s/

.PHONY: k8s-delete
k8s-delete:
    kubectl delete -f k8s/

# ============================
# Utility
# ============================

.PHONY: clean
clean:
    rm -rf __pycache__ */__pycache__ .pytest_cache
