# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from config import settings
from optimum.graphcore import pipeline

model = "distilbert-base-cased-distilled-squad"
pipe = pipeline("question-answering", model=model)


def compile(pipe):
    pipe(question="What is your name?", context="My name is Rob.")
    return
