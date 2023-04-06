# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
from importlib import reload
import time
import pytest
from fastapi.testclient import TestClient


class TestServerBase:
    app = None

    @classmethod
    def reload_server(self):
        import config

        reload(config)
        import server

        self.app = reload(server).app

    def wait_server_ready(self):
        print("Waiting for test server to be ready...")
        while True:
            time.sleep(5)
            response = self.test_client.get("/health/readiness/")
            if response.status_code == 200:
                break

    def setup_class(self):
        print(f"setup_class called for the {self.__name__}")
        self.reload_server()
        self.test_client = TestClient(self.app)
        self.test_client = self.test_client.__enter__()
        self.wait_server_ready(self)

    def teardown_class(self):
        print(f"teardown_class called for the {self.__name__}")
        self.test_client.__exit__()

    @pytest.fixture
    def client(self):
        return self.test_client
