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
  apt-get install -y kafkacat && \
  apt-get install -y ffmpeg libsm6 libxext6 && \
  # apt-get install -y libc6-dev-arm64-cross&&\
  apt-get install -y ca-certificates && \
  # wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh && \
  wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-py311_23.11.0-2-Linux-x86_64.sh -O /opt/miniconda.sh && \
  /bin/bash /opt/miniconda.sh -b -p /opt/conda

ENV CONDA_DIR /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda init && \
    /bin/bash && \
    # conda install -y -c conda-forge libmamba libarchive gxx root=6.30.8

    conda install -y -c conda-forge libmamba libarchive gxx root=6.28.0
#libmamba=1.5.5 libarchive=3.7.2 gxx=11.4.

RUN pip install requests psycopg2-binary sqlalchemy kafka-python-ng && apt-get update && apt-get install -y kafkacat

ENV PYTHONUNBUFFERED=1
WORKDIR /app/worker
CMD ["./wait-for-kafka.sh", "./entrypoint.sh"]
