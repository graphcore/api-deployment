# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import pytest
import sys
import os
from fastapi.testclient import TestClient

TESTS_DIRECTORY = os.path.dirname(__file__)
SRC_DIRECTORY = os.path.join(TESTS_DIRECTORY, "..")
sys.path.append(SRC_DIRECTORY)
from server import app


test_client = TestClient(app)


def pytest_sessionstart(session):
    global test_client
    test_client = test_client.__enter__()
    return


def pytest_sessionfinish(session):
    global test_client
    test_client.__exit__()
    return


@pytest.fixture
def client():
    global test_client
    return test_client
