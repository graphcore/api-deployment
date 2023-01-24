#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Utility to check the app server is running.
# This can be used to check or wait for availability.
# A timeout can be specified.

SN=${BASH_SOURCE[0]}
BSN=$(basename $SN)
if [ "${SN}" != "${0}" ]; then
 echo "Script ${BSN} MUST be executed. Use \"$ ./${BSN}\""
 return
fi

if [[ -z "$SERVER_PORT" ]]; then
  SERVER_PORT="${1:-8100}"
  echo "SERVER_PORT ${SERVER_PORT} from argument 1"
else
  echo "SERVER_PORT ${SERVER_PORT} from environment variable"
fi

if [[ -z "$SERVER_WAIT_TIMEOUT" ]]; then
  SERVER_WAIT_TIMEOUT="${2:-300}"
  echo "SERVER_WAIT_TIMEOUT ${SERVER_WAIT_TIMEOUT} from argument 1"
else
  echo "SERVER_WAIT_TIMEOUT ${SERVER_WAIT_TIMEOUT} from environment variable"
fi

source utils/set_default_inet.sh
RUN_RESULT=$?
if [ $RUN_RESULT -ne 0 ]; then
  echo "Error: Issue establishing inet address"
  exit $RUN_RESULT
fi

echo "Server expected at ${DEFAULT_INET}:${SERVER_PORT}"

echo "Waiting for server ready"

WAIT_TIME=0

while true; do
  CHECK=$(curl $DEFAULT_INET:$SERVER_PORT 2> /dev/null)
  READY=$(echo $CHECK | grep "Health Check Passed!" | wc -l)

  if [ "$READY" -gt 0 ]
  then
    echo "Ready"
    echo "SERVER : ${DEFAULT_INET}:${SERVER_PORT}"
    exit 0
  fi

  if [ "$WAIT_TIME" -gt $SERVER_WAIT_TIMEOUT ]
  then
    echo " Timeout"
    exit 124
  fi

  sleep 5
  WAIT_TIME=$((WAIT_TIME + 5))
done
