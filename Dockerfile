FROM nvidia/cuda:12.6.3-devel-ubuntu22.04 AS  build

RUN apt-get update && apt-get install -y build-essential git cmake git-lfs software-properties-common &&  add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y  \
ca-certificates \
libsndfile1-dev \
libgl1 \
python3.10 \
python3.10-dev \
python3-pip \
python3.10-venv && \
rm -rf /var/lib/apt/lists


RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN CMAKE_ARGS="-DSD_CUBLAS=ON" pip install stable-diffusion-cpp-python


FROM nvidia/cuda:12.6.3-base-ubuntu20.04 AS runtime

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y  \
python3.10 \
python3.10-venv && \
rm -rf /var/lib/apt/lists

COPY --from=build [ "/opt/venv", "/opt/venv" ]

ENV PATH="/opt/venv/bin:$PATH"

