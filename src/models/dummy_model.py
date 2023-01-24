# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import time


class Pipeline:
    def __call__(self, inputs):
        time.sleep(0.001)
        return inputs


def compile(pipe: Pipeline):
    return


pipe = Pipeline()
