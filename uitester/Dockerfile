FROM python:3.10.16-slim-bookworm

COPY requirements.txt /home

WORKDIR /home

RUN pip install -r requirements.txt

COPY app.py /home

EXPOSE 8000

CMD ["python", "-m", "chainlit", "run", "app.py", "-h","--host","0.0.0.0"]