# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
from optimum.graphcore import IPUConfig
from optimum.graphcore import pipeline

ipu_config = IPUConfig(
    layers_per_ipu=[24], matmul_proportion=0.15, executable_cache_dir="./exe_cache"
)


class SummarizationPipeline:
    def __init__(self):
        self.summarization_pipeline = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn",
            ipu_config=ipu_config.to_dict(),
            config="facebook/bart-large-cnn",
            num_beams=3,
            input_max_length=500,
            truncation=True,
            max_length=100,
        )

    def __call__(self, input_dict):
        input_str = input_dict["documents"]
        result = self.summarization_pipeline(input_str, truncation="only_first")
        return {"summary": result}


def compile(pipe: SummarizationPipeline):
    pipe({"documents": "Just compile"})
    return


pipe = SummarizationPipeline()
compile(pipe)
