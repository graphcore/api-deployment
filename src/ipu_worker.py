# Copyright (c) 2022 Graphcore Ltd. All rights reserved.
import importlib
import multiprocessing as mp
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List
from config import ModelConfig


@dataclass
class IPUWorker:
    """Class to hold a single model and basic inference features"""

    """ A pipe can vary depending on model/task, and must be implemented in the model file"""
    model_name: str
    replicas: int
    input_queue: mp.Queue
    output_queue: mp.Queue
    ready: mp.Event = None
    barrier: mp.Barrier = None

    def start(self):
        self.ready = mp.Event()
        self.barrier = mp.Barrier(self.replicas)
        self.processes = [
            mp.Process(
                target=self.process_loop,
                args=(self.input_queue, self.output_queue, self.ready, self.barrier),
            )
            for _ in range(self.replicas)
        ]
        [p.start() for p in self.processes]
        self.missing = {}

    def stop(self):
        [p.kill() for p in self.processes if p]

    def process_loop(
        self,
        input_queue: mp.Queue,
        output_queue: mp.Queue,
        ready: mp.Event,
        barrier: mp.Barrier,
    ):
        print("Process started")
        # ! The pipeline must be imported inside the process
        m = importlib.import_module("models." + self.model_name)
        self.pipe = m.Pipeline()
        self.pipe.compile()
        if barrier and barrier.wait() == 0:
            ready.set()
        while True:
            thread_id, inputs = input_queue.get()
            chrono_start = time.time()
            results = self.pipe(inputs)
            chrono = time.time() - chrono_start
            results["model_latency"] = chrono
            output_queue.put([thread_id, results])

    def feed(self, data_dict: Dict):
        thread_id = threading.get_ident()
        self.input_queue.put([thread_id, data_dict])

    def get_result(self):
        result = None
        while True:
            if str(threading.get_ident()) in self.missing:
                result = self.missing[str(threading.get_ident())]
                del self.missing[str(threading.get_ident())]
                break
            else:
                pass
            try:
                result = self.output_queue.get(timeout=0.001)
                if result[0] != threading.get_ident():
                    # Handle synchronisation issues
                    # If the message was not for this thread
                    # Put the message in a dict so the other threads can find it in quicker time
                    self.missing[str(result[0])] = result
                else:
                    break
            except:
                pass
        return result[1]

    def queue_size(self):
        return self.input_queue.qsize()

    def is_alive(self):
        return all([process.is_alive() for process in self.processes])


@dataclass
class IPUWorkerGroup:
    """Class to hold a list of running models"""

    model_list: List[ModelConfig]
    workers: Dict[str, IPUWorker] = field(default_factory=dict)
    started_with_no_exception: bool = True
    is_compiled: bool = False
    is_cancelled: bool = False

    def is_ready(self):
        if len(self.workers.values()) == 0:
            return False
        return all([w.ready.is_set() for w in self.workers.values()])

    def is_alive(self):
        if not self.is_compiled:
            return self.started_with_no_exception
        else:
            return all([w.is_alive() for w in self.workers.values()])

    def start(self):
        try:
            for model_config in self.model_list:

                self.workers.update(
                    {
                        model_config.model: IPUWorker(
                            model_name=model_config.model,
                            replicas=model_config.replicas,
                            input_queue=mp.Queue(),
                            output_queue=mp.Queue(),
                        )
                    }
                )

            [w.start() for w in self.workers.values()]

            # Wait for workers to be ready
            while True:
                time.sleep(1)
                if not all([w.is_alive() for w in self.workers.values()]):
                    raise Exception("A worker process failed to start")
                if self.is_ready():
                    print("All workers are ready")
                    break
                if self.is_cancelled:
                    print("Workers startup cancelled")
                    break
            self.is_compiled = True
        except Exception as e:
            self.started_with_no_exception = False
            print("IPU worker group start failed with: ", e)
        return

    def stop(self):
        [w.stop() for w in self.workers.values()]
        self.is_cancelled = True
        return
