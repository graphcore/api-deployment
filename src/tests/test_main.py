# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import time

from test_server_base import TestServerBase


class Timer:
    def __init__(self):
        self.time = 0

    def __enter__(self):
        self.time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.time = time.time() - self.time
        if hasattr(self, "q"):
            self.q.append(self.time)

    def set_buffer(self, q):
        self.q = q


class TestApi(TestServerBase):
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_summarization(self, client):
        errors = []
        params = {"documents": "This is just a test."}

        response = client.post("/summarization", json=params)
        if response.status_code != 200:
            errors.append(f"HTTP response status code is not {200}")
        if "results" not in response.json().keys():
            errors.append(f"'results' key absent from response")
        if not len(errors) == 0:
            raise Exception(f"TEST FAILED errors:\n{errors}")

    def test_qa(
        self, client, num=100, error_q=None, latency_q=None, response_time_q=None
    ):
        errors = 0
        names = ["John", "Alice", "Rachid"]
        params = {"context": "", "question": "What is his name?"}
        for k in range(num):
            params["context"] = "His name is " + names[k % 3]
            with Timer() as timer:
                response = client.post("/qa", json=params)
                if response_time_q is not None:
                    timer.set_buffer(response_time_q)
            try:
                if not response.json()["results"] == names[k % 3]:
                    errors += 1
                if latency_q is not None:
                    latency_q.append(float(response.headers["metrics-worker-latency"]))
            except Exception as e:
                raise type(e)(str(e) + " with response " + str(response))
            assert response.status_code == 200
            if not error_q:
                assert errors == 0
            else:
                error_q.append(errors)

    def test_readiness(self, client):
        response = client.get("/health/readiness")
        assert response.status_code == 200

    def test_startup(self, client):
        response = client.get("/health/startup")
        assert response.status_code == 200

    def test_liveness(self, client):
        response = client.get("/health/liveness")
        assert response.status_code == 200
