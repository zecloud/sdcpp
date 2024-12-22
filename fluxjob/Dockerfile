#FROM zecloud.azurecr.io/sdcppcuda:final
FROM zecloud.azurecr.io/sdcppcuda:fnotinative

# RUN apt-get update \
#     && apt-get install -y libgomp1 libcublas-12-6

# ENV LD_LIBRARY_PATH=/usr/local/cuda-12.6/compat/:$LD_LIBRARY_PATH

# # # Set CUDA_HOME environment variable
# ENV CUDA_HOME=/usr/local/cuda
# # # Update PATH to include CUDA binalsries
# ENV PATH=${CUDA_HOME}/bin:${PATH}
# # # Update LD_LIBRARY_PATH to include CUDA libraries
# ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

COPY requirements.txt /home

WORKDIR /home

RUN pip install -r requirements.txt

COPY job.py /home

COPY msgprocessor.py /home

COPY blockprocessor.py /home

COPY queueprocessor.py /home

ENTRYPOINT ["python", "job.py"]