FROM zecloud.azurecr.io/sdcppcuda:fnotinative

COPY requirements.txt /home

WORKDIR /home

RUN pip install -r requirements.txt

COPY app.py /home

ENTRYPOINT ["python", "app.py"]