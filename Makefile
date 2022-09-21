.PHONY: all docker_image
all: docker_image

IMAGE := $(notdir $(CURDIR))
TAG := "0.0.1-dev"

docker_image:
	docker build -t $(IMAGE):$(TAG) .