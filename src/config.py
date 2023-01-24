# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    server_models: List[str] = ["summarization", "question_answering"]

    class Config:
        env_file = "../.env"


settings = Settings()
