#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Run the server for this project.
set -o nounset
set -o pipefail
set -o errexit


SN=${BASH_SOURCE[0]}
BSN=$(basename $SN)
if [ "${SN}" != "${0}" ]; then
 echo "Script ${BSN} MUST be executed. Use \"$ ./${BSN}\""
 return
fi

# Usage:
#
# $ ./run_server.sh <SERVER_PORT> <SERVER_NUM_WORKERS> <SERVER_BACKGROUND>
#
# Example:
#
# $ ./run_server.sh 8000 1 1
#
# If <SERVER_BACKGROUND> is set then the script will background the server process
# but only exit once the server is fully up and available.

if [[ -z "${SERVER_PORT:-}" ]]; then
  SERVER_PORT="${1:-8100}"
  echo "SERVER_PORT ${SERVER_PORT} from argument 1"
else
  echo "SERVER_PORT ${SERVER_PORT} from environment variable"
fi

if [[ -z "${SERVER_NUM_WORKERS:-}" ]]; then
  SERVER_NUM_WORKERS="${2:-1}"
  echo "SERVER_NUM_WORKERS ${SERVER_NUM_WORKERS} from argument 2"
else
  echo "SERVER_NUM_WORKERS ${SERVER_NUM_WORKERS} from environment variable"
fi

if [[ -z "${SERVER_BACKGROUND:-}" ]]; then
  SERVER_BACKGROUND="${3:-0}"
  echo "SERVER_BACKGROUND ${SERVER_BACKGROUND} from argument 3"
else
  echo "SERVER_BACKGROUND ${SERVER_BACKGROUND} from environment variable"
fi

# -- Start (background) or run server --

source ./utils/set_default_inet.sh

pushd src
if [ $SERVER_BACKGROUND -ne 0 ]; then
  echo "Starting server as background job ..."
  uvicorn server:app --host "0.0.0.0" --port $SERVER_PORT --workers $SERVER_NUM_WORKERS &
  popd
  RUN_RESULT=$?
  SERVER_PID=$!
  echo "SERVER_PID : ${SERVER_PID}"
  if [ $RUN_RESULT -ne 0 ]; then
    echo "Error: Issue starting server"
    kill $SERVER_PID
    echo "RUN_RESULT : ${RUN_RESULT}"
    exit $RUN_RESULT
  fi
  echo "Starting server as background job ... done"
  ./utils/check_wait_server.sh $SERVER_PORT
  RUN_RESULT=$?
  if [ $RUN_RESULT -ne 0 ]; then
    echo "Error: Issue syncing server"
    kill $SERVER_PID
  else
    echo "PID : ${SERVER_PID} (Use '$ kill ${SERVER_PID}' to stop it)"
    echo "Running server on ${DEFAULT_INET}:${SERVER_PORT}"
    echo "See ${DEFAULT_INET}:${SERVER_PORT}/docs"

  fi
else
  echo "Running server on ${DEFAULT_INET}:${SERVER_PORT}"
  echo "See ${DEFAULT_INET}:${SERVER_PORT}/docs"
  uvicorn server:app --host "0.0.0.0" --port $SERVER_PORT --workers $SERVER_NUM_WORKERS
  RUN_RESULT=$?
fi

echo "RUN_RESULT : ${RUN_RESULT}"
exit $RUN_RESULT
