.PHONY: all docker_image
all: docker_image

IMAGE := $(notdir $(CURDIR))
TAG := "0.0.2-dev"

docker_image:
	docker build -t $(IMAGE):$(TAG) .