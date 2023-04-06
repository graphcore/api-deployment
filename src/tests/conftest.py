# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import pytest
import sys
import os
from fastapi.testclient import TestClient

TESTS_DIRECTORY = os.path.dirname(__file__)
SRC_DIRECTORY = os.path.join(TESTS_DIRECTORY, "..")
sys.path.append(SRC_DIRECTORY)
