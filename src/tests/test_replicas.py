# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import multiprocessing
import os

import pytest

from test_server_base import TestServerBase


class TestReplicas(TestServerBase):
    numberOfReplicas = 3

    @pytest.fixture(autouse=True, scope="module")
    def _prepare(self):
        os.environ["SERVER_MODELS"] = (
            '[{"model":"question_answering","replicas":"'
            + str(self.numberOfReplicas)
            + '"}]'
        )

    def test_replicas_request(self, client):
        assert len(multiprocessing.active_children()) == self.numberOfReplicas
        params = {"context": "His name is Tom.", "question": "What is his name?"}

        response = client.post("/qa", json=params)
        assert response.status_code == 200
