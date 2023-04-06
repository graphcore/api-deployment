# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api_classes import *
import time
from ipu_worker import IPUWorkerGroup
from config import settings
from threading import Thread

app = FastAPI()

models = settings.server_models
model_names = [model.model for model in models]
w = IPUWorkerGroup(model_list=models)
compilation = Thread(target=w.start)


@app.on_event("startup")
def startup_event():
    compilation.start()
    print("Running the following models:", model_names)
    return


@app.on_event("shutdown")
def shutdown_event():
    # Handle early errors, if workers were still compiling:
    if compilation.is_alive():
        time.sleep(2)
        w.stop()
        compilation.join()
    w.stop()
    return


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "Health Check Passed!"}


@app.post("/summarization", include_in_schema="summarization" in model_names)
def run_summarization(model_input: SummarizationInput):
    latency = time.time()

    data_dict = model_input.dict()
    w.workers["summarization"].feed(data_dict)
    result = w.workers["summarization"].get_result()

    latency = time.time() - latency

    headers = {"metrics-latency": str(latency)}
    response = {
        "results": result["summary"],
    }
    return JSONResponse(content=response, headers=headers)


@app.post("/qa", include_in_schema="question_answering" in model_names)
def run_qa(model_input: QA):
    latency = time.time()

    data_dict = model_input.dict()
    w.workers["question_answering"].feed(data_dict)
    result = w.workers["question_answering"].get_result()

    latency = time.time() - latency

    headers = {"metrics-latency": str(latency)}
    response = {
        "results": result["answer"],
        "score": result["score"],
    }
    return JSONResponse(content=response, headers=headers)


# The readiness health check is meant to inform
# whether the server is ready to receive requests or not
@app.get("/health/readiness/", status_code=status.HTTP_200_OK)
def readiness_check(response: Response):
    message = "Readiness check succeeded."
    if not w.is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Readiness check failed."
    return {"message": message}


# As soon as we start the server, the endpoints are ready to be read
@app.get("/health/startup/", status_code=status.HTTP_200_OK)
def startup_check():
    return {"message": "Startup check succeeded."}


# The liveness health check is meant to detect unrecoverable errors
# the server needs restart if unhealthy state is detected
@app.get("/health/liveness/", status_code=status.HTTP_200_OK)
def liveness_check(response: Response):
    message = "Liveness check succeeded."
    if not w.is_alive():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        message = "Liveness check failed."
    return {"message": message}
