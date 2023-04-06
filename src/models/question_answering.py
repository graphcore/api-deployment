# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from optimum.graphcore import pipeline


class Pipeline:
    def __init__(self):
        self.qa_pipeline = pipeline(
            "question-answering", model="distilbert-base-cased-distilled-squad"
        )

    def __call__(self, input_dict):
        result = self.qa_pipeline(input_dict)
        return result

    def compile(self):
        # Model is compiled on the first call
        dummy_inputs_dict = {
            "question": "What is your name?",
            "context": "My name is Rob.",
        }
        self(dummy_inputs_dict)
        return
