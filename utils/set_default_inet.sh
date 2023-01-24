#!/usr/bin/env bash
# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
# Utility to establish default interface and inet address.
# On return DEFAULT_INET and DEFAULT_IFACE will be set.

if ! [ -x "$(command -v ip)" ]; then
USE_NET_TOOLS=true
else
USE_NET_TOOLS=false
fi

if [ $USE_NET_TOOLS == true ]; then
echo "Using net tools"
DEFAULT_IFACE=$(route | grep default | head -1 | awk '{print $8}')
DEFAULT_INET=$(ifconfig $DEFAULT_IFACE | grep " inet " | head -1 | awk '{print $2}')
else
echo "Using ip"
DEFAULT_IFACE=$(ip route show | grep default | head -1 | awk '{print $5}')
DEFAULT_INET=$(ip route show | grep -v default | grep " ${DEFAULT_IFACE} " | head -1 | awk '{print $NF}')
fi

# These strings are checked for by the tests.
echo "DEFAULT_IFACE : ${DEFAULT_IFACE}"
echo "DEFAULT_INET : ${DEFAULT_INET}"
