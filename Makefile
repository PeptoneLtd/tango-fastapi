.PHONY: all docker_image
all: docker_image

REGISTRY := ghcr.io/peptoneltd
IMAGE := $(notdir $(CURDIR))
TAG := 0.0.4-dev

docker_image:
	docker build --platform=linux/amd64 -t $(REGISTRY)/$(IMAGE):$(TAG) .

push:
	docker push $(REGISTRY)/$(IMAGE):$(TAG)
