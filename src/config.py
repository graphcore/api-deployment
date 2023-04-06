# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from pydantic import BaseSettings, BaseModel
from typing import List

DEFAULT_REPLICA_NUMBER: int = 1


class ModelConfig(BaseModel):
    model: str
    replicas: int = DEFAULT_REPLICA_NUMBER


class Settings(BaseSettings):
    server_models: List[ModelConfig] = [
        {"model": "summarization"},
        {"model": "question_answering"},
    ]

    class Config:
        env_file = "../.env"


settings = Settings()
