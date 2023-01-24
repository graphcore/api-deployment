#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Utility to install latest docker-compose.

SN=${BASH_SOURCE[0]}
BSN=$(basename $SN)
if [ "${SN}" == "${0}" ]; then
 echo "Script ${BSN} MUST be sourced. Use \"$ . ${BSN}\""
 exit
fi

# Helper function to test versions.
# Returns true (0) iff $A <= $B for versionlte $A $B
versionlte() {
    [ "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

# Helper function to test versions.
# Returns true (0) iff $A < $B for versionlte $A $B
versionlt() {
    [ "$1" = "$2" ] && return 1 || versionlte $1 $2
}

# Set path.
# NOTE:
# It would be neater to download docker-compose to a specific directory
# (e.g. ~/.local/bin) but this fails when running in a GHA VM with errors like:
# 'Cannot open self <path>/docker-compose or archive <path>/docker_compose/docker-compose.pkg'
# Downloading it the CWD works around this issue.
DOCKER_COMPOSE_DESTINATION_FOLDER=.
DOCKER_COMPOSE_DESTINATION=${DOCKER_COMPOSE_DESTINATION_FOLDER}/docker-compose
PATH=${DOCKER_COMPOSE_DESTINATION_FOLDER}:$PATH

# Establish installed version.
if ! command -v docker-compose &> /dev/null
then
  DOCKER_COMPOSE_VERSION="v0.0.0"
  DOCKER_COMPOSE_VERSION_NO="0.0.0"
else
  echo "Installed:"
  docker-compose --version
  DOCKER_COMPOSE_VERSION=$(docker-compose --version | head -n1)
  DOCKER_COMPOSE_VERSION_NO=$(echo $DOCKER_COMPOSE_VERSION | grep -Eo "[0-9]+.[0-9]+.[0-9]+")
  echo "(extracted as ${DOCKER_COMPOSE_VERSION_NO})"
fi

# Establish latest version.
DOCKER_COMPOSE_LATEST_VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*\d')
echo "Latest:"
echo ${DOCKER_COMPOSE_LATEST_VERSION}
DOCKER_COMPOSE_LATEST_VERSION_NO=$(echo $DOCKER_COMPOSE_LATEST_VERSION | grep -Eo "[0-9]+.[0-9]+.[0-9]+")
echo "(extracted as ${DOCKER_COMPOSE_LATEST_VERSION_NO})"

# Install if there is a newer version.
if versionlt $DOCKER_COMPOSE_VERSION_NO $DOCKER_COMPOSE_LATEST_VERSION_NO; then
  echo "Installing: ${DOCKER_COMPOSE_LATEST_VERSION}"
  echo "Fetching ... "
  rm -f $DOCKER_COMPOSE_DESTINATION
  mkdir -p $DOCKER_COMPOSE_DESTINATION_FOLDER
  curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_LATEST_VERSION}/docker-compose-$(uname -s)-$(uname -m) > $DOCKER_COMPOSE_DESTINATION
  chmod +x $DOCKER_COMPOSE_DESTINATION
  ls -lat $DOCKER_COMPOSE_DESTINATION
  $DOCKER_COMPOSE_DESTINATION --version
  echo "Fetching ... done"
  echo "Installed:"
  which docker-compose
  docker-compose --version
fi
