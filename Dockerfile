# Copyright (c) 2023 Graphcore Ltd. All rights reserved.

# set base image (host OS)
FROM graphcore/pytorch:3.1.0-ubuntu-20.04-20221218
WORKDIR .

RUN apt-get -y update
RUN apt-get -y install git

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY utils ./utils
COPY run_*.sh ./

CMD ./run_server.sh
