# These can be overidden with env vars.
REGISTRY ?= cluster-registry:5000
IMAGE_NAME ?= products
IMAGE_TAG ?= latest
IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
PLATFORM ?= "linux/amd64,linux/arm64"
CLUSTER ?= nyu-devops


.SILENT:

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

##@ Development

.PHONY: clean
clean:	## Removes all dangling build cache
	$(info Removing all dangling build cache..)
	-docker rmi $(IMAGE)
	docker image prune -f
	docker buildx prune -f

.PHONY: venv
venv: ## Create a Python virtual environment
	$(info Creating Python 3 virtual environment...)
	pipenv shell

.PHONY: install
install: ## Install dependencies
	$(info Installing dependencies...)
	sudo pipenv install --system --dev

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
	pylint service tests --max-line-length=127

.PHONY: test
test: ## Run the unit tests
	$(info Running tests...)
	export RETRY_COUNT=1; pytest --pspec --cov=service --cov-fail-under=95

##@ Runtime

.PHONY: run
run: ## Run the service
	$(info Starting service...)
	honcho start

.PHONY: secret
secret: ## Generate a secret hex key
	$(info Generating a new secret key...)
	python3 -c 'import secrets; print(secrets.token_hex())'

##@ Kubernetes

.PHONY: cluster
cluster: ## Create a K3D Kubernetes cluster with load balancer and registry
	$(info Creating Kubernetes cluster $(CLUSTER) with a registry and 1 worker node...)
	k3d cluster create $(CLUSTER) --agents 1 --registry-create cluster-registry:0.0.0.0:5000 --port '8080:80@loadbalancer'

.PHONY: cluster-rm
cluster-rm: ## Remove a K3D Kubernetes cluster
	$(info Removing Kubernetes cluster $(CLUSTER)...)
	k3d cluster delete $(CLUSTER)

.PHONY: tekton
tekton: ## Install Tekton
	$(info Installing Tekton in the Cluster...)
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases/dashboard/latest/tekton-dashboard-release.yaml

.PHONY: clustertasks
clustertasks: ## Create Tekton Cluster Tasks
	$(info Creating Tekton Cluster Tasks...)
	wget -qO - https://raw.githubusercontent.com/tektoncd/catalog/main/task/openshift-client/0.2/openshift-client.yaml | sed 's/kind: Task/kind: ClusterTask/g' | kubectl create -f -
	wget -qO - https://raw.githubusercontent.com/tektoncd/catalog/main/task/buildah/0.4/buildah.yaml | sed 's/kind: Task/kind: ClusterTask/g' | kubectl create -f -

.PHONY: knative
knative: ## Install Knative
	$(info Installing Knative in the Cluster...)
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.8.3/serving-crds.yaml
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.8.3/serving-core.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.8.5/eventing-crds.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.8.5/eventing-core.yaml

.PHONY: deploy
deploy: ## Deploy the service on local Kubernetes
	$(info Deploying service locally...)
	kubectl apply -R -f k8s/

############################################################
# COMMANDS FOR BUILDING THE IMAGE
############################################################

##@ Image Build

.PHONY: init
init: export DOCKER_BUILDKIT=1
init:	## Creates the buildx instance
	$(info Initializing Builder...)
	-docker buildx create --use --name=qemu
	docker buildx inspect --bootstrap

.PHONY: build
build:	## Build all of the project Docker images
	$(info Building $(IMAGE) for $(PLATFORM)...)
	docker build --rm --pull --tag $(IMAGE) .

.PHONY: push
push:	## Push the image to the container registry
	$(info Pushing $(IMAGE)...)
	docker push $(IMAGE)

.PHONY: buildx
buildx:	## Build multi-platform image with buildx
	$(info Building multi-platform image $(IMAGE) for $(PLATFORM)...)
	docker buildx build --file Dockerfile  --pull --platform=$(PLATFORM) --tag $(IMAGE) --push .

.PHONY: remove
remove:	## Stop and remove the buildx builder
	$(info Stopping and removing the builder image...)
	docker buildx stop
	docker buildx rm
