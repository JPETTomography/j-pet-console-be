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
  apt-get install -y netcat &&\
  apt-get install -y ffmpeg libsm6 libxext6 && \
  apt-get install -y ca-certificates && \
  wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-py311_23.11.0-2-Linux-x86_64.sh -O /opt/miniconda.sh && \
  /bin/bash /opt/miniconda.sh -b -p /opt/conda

ENV CONDA_DIR /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda init && \
    /bin/bash && \
    conda install -y -c conda-forge libmamba=1.5.8 libarchive=3.7.4 gxx=11.4.0 root=6.28.0

RUN pip install requests psycopg2-binary==2.9.10 watchdog==3.0.0 passlib pika && apt-get update

ADD . /app
WORKDIR /app/
CMD ["./common/wait-for-rabbit.sh","./agent/entrypoint.sh"]
