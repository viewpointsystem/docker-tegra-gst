SHELL := /bin/bash

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


setup:
	mkdir -p common/gst
	mkdir -p common/lib
	cp /usr/lib/aarch64-linux-gnu/gstreamer-1.0/libgstnv* common/gst
	cp /usr/lib/aarch64-linux-gnu/libgstnv* common/lib

build: ## Build the container
	docker-compose build gst

shell:
	docker-compose run gst /bin/bash

run:
	docker-compose run gst 