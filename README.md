# docker-tegra-gst
Small dockerized gstreamer application for arm64/tegra

## Goal of the project

This is a small application to test gstreamer functionality
with nvidia hardware (omx) inside a docker container. 

This container does not make use of nvidia-docker,
and therefore is compatible with earlier L4T versions.

## Status

Currently it only tests omx plugin with `nvoverlay` and `nvconvert` 
We are planning on adding several tests including encoding. 

## Getting started

You need gstreamer and the nvidia gstreamer plugins installed on the host
to build this image, or copy them into `./common`

Before building, run `make setup` to copy the nvidia plugins into common.

And then run `make build` to build the container.

To run the gstreamer in container test using omx run: `docker-compose run gst`


## Known issues

- Sometimes the encoder fails to allocate memory from within docker.
Current workaround is to initialize the encoder from outside the container first.

## Further links

https://github.com/NVIDIA/nvidia-docker
