#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Run server from docker image.

# use the .env file
set -o allexport; source .env; set +o allexport
DOCKER_IMAGE_NAME=${COMPOSE_PROJECT_NAME}-models

# Make sure docker compose is available on this system.
source ./utils/install_latest_docker_compose.sh

# Status
echo "Docker status (before)"
docker image ls | grep --color "${DOCKER_IMAGE_NAME}\|$"
docker ps | grep --color "${DOCKER_IMAGE_NAME}\|$"

# Make sure image doesn't exist already (remove it).
# This should also stop existing running containers.
echo "Removing existing image ..."
docker rmi --force ${DOCKER_IMAGE_NAME}
docker rmi $(docker images --filter dangling=true -q --no-trunc)
echo "Removing existing image ... done"

# Build the image.
echo "Building image ..."
docker-compose build
RUN_RESULT=$?
echo "Building image ... done"
if [ $RUN_RESULT -ne 0 ]; then
    echo "Error: Failure in docker load"
    exit $RUN_RESULT
fi

# Start it.
echo "Running docker-compose up ..."
docker-compose up --detach
RUN_RESULT=$?
echo "Running docker-compose up ... done"
if [ $RUN_RESULT -ne 0 ]; then
    echo "Error: Failure in docker-compose up"
    exit $RUN_RESULT
fi

echo "Docker status (after)"
docker image ls | grep --color "${DOCKER_IMAGE_NAME}\|$"
docker ps | grep --color "${DOCKER_IMAGE_NAME}\|$"

# DOCKER_ID=$(docker ps -aqf "name=${COMPOSE_PROJECT_NAME}")
# echo $DOCKER_ID
# Wait for server
./utils/check_wait_server.sh
