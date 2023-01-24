# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from pydantic import BaseModel

# Summarization
class SummarizationInput(BaseModel):
    documents: str


# Question/Answer
class QA(BaseModel):
    context: str
    question: str
