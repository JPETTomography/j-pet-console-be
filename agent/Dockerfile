FROM python:3.11-slim

WORKDIR /app/agent


# HOW TO:
# Build image (from the directory containing dockerfile):
# docker build --tag 'ubuntu-g4:22.04-11.03' .
# Run container:
# docker run -ti --rm ubuntu-g4:22.04-11.03 /bin/bash

FROM ubuntu:22.04
RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker
RUN DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  #apt-get install -y build-essential && \
  apt-get install -y wget && \
  apt-get install -y gpg && \
  apt-get install -y cmake && \
  apt-get install -y git && \
  apt-get install -y curl && \
  apt-get install -y ca-certificates && \
  wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh && \
  /bin/bash /opt/miniconda.sh -b -p /opt/conda

ENV CONDA_DIR /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda init && \
    /bin/bash && \
    conda install -y -c conda-forge libmamba libarchive gxx root

RUN pip install requests kafka-python-ng && apt-get update && apt-get install -y kafkacat
CMD ["./wait-for-kafka.sh", "python", "agent.py"]
