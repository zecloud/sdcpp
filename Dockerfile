FROM nvidia/cuda:12.6.3-devel-ubuntu22.04 AS  build

RUN apt-get update && apt-get install -y build-essential git cmake git-lfs software-properties-common &&  add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y  \
    ca-certificates \
    libsndfile1-dev \
    libgl1 \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-venv libgomp1 && \
    rm -rf /var/lib/apt/lists   

RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip wheel
#RUN CMAKE_ARGS="-DSD_CUBLAS=ON -DGGML_NATIVE=ON" pip install --verbose stable-diffusion-cpp-python
#COPY ./stable-diffusion-cpp-python /stable-diffusion-cpp-python
RUN CMAKE_ARGS="--DSD_CUDA=ON -DGGML_NATIVE=OFF" pip install --verbose stable-diffusion-cpp-python

#RUN pip install --upgrade pip wheel
#RUN CMAKE_ARGS="-DSD_CUBLAS=ON" pip wheel --verbose --no-cache-dir --wheel-dir /sdcppwheel stable-diffusion-cpp-python

FROM nvidia/cuda:12.6.3-base-ubuntu22.04 AS runtime

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y  \
python3.10 \
python3.10-venv \
  && \ 
rm -rf /var/lib/apt/lists
#libcublas-12-6 libgomp1
#RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#COPY --from=build /sdcppwheel /sdcppwheel
#RUN pip install --no-cache-dir --no-index --find-links=/sdcppwheel  /sdcppwheel/*

#apt-get install libgomp1 libcublas-12-6
#ENV LD_LIBRARY_PATH=/usr/local/cuda-12.6/compat/:$LD_LIBRARY_PATH
COPY --from=build [ "/opt/venv", "/opt/venv" ]


ENV LD_LIBRARY_PATH=/usr/local/lib
COPY --from=build /usr/lib/x86_64-linux-gnu/libgomp.so.1 ${LD_LIBRARY_PATH}/libgomp.so.1
COPY --from=build /usr/local/cuda/lib64/libcublas.so.12 ${LD_LIBRARY_PATH}/libcublas.so.12
COPY --from=build /usr/local/cuda/lib64/libcublasLt.so.12 ${LD_LIBRARY_PATH}/libcublasLt.so.12
COPY --from=build /usr/local/cuda/lib64/libcudart.so.12 ${LD_LIBRARY_PATH}/libcudart.so.12


# # Set CUDA_HOME environment variable
#ENV CUDA_HOME=/usr/local/cuda
# # Update PATH to include CUDA binalsries
#ENV PATH=${CUDA_HOME}/bin:${PATH}
# # Update LD_LIBRARY_PATH to include CUDA libraries
#ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# # Copy CUDA libraries from the build stage to the runtime stage
# COPY --from=build ${CUDA_HOME}/lib64 /usr/local/cuda/lib64
# COPY --from=build /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/local/cuda/lib64
# COPY --from=build /usr/local/cuda-12.6/targets/x86_64-linux/lib/libcublas.so.12 /usr/local/cuda/lib64
# COPY --from=build /usr/local/cuda-12.6/targets/x86_64-linux/lib/libcudart.so.12 /usr/local/cuda/lib64
# COPY --from=build /usr/local/cuda-12.6/targets/x86_64-linux/lib/libcublasLt.so.12 /usr/local/cuda/lib64

#ENV PATH="/opt/venv/bin:$PATH"


