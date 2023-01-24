#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Stop server from docker image.
# i.e. It will be executed on remote target to stop an image.

# use the .env file
set -o allexport; source .env; set +o allexport
DOCKER_IMAGE_NAME=${COMPOSE_PROJECT_NAME}-models

# Make sure docker compose is available on this system.
source ./utils/install_latest_docker_compose.sh

# Status
echo "Docker status (before)"
docker image ls | grep --color "${DOCKER_IMAGE_NAME}\|$"
docker ps | grep --color "${DOCKER_IMAGE_NAME}\|$"

# Stop it.
echo "Running docker-compose down ..."
docker-compose down
RUN_RESULT=$?
echo "Running docker-compose down ... done"
if [ $RUN_RESULT -ne 0 ]; then
    echo "Error: Failure packing repo"
    exit $RUN_RESULT
fi

# Status
echo "Docker status (after)"
docker image ls | grep --color "${DOCKER_IMAGE_NAME}\|$"
docker ps | grep --color "${DOCKER_IMAGE_NAME}\|$"
