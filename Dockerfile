FROM python:3.9

WORKDIR /app
COPY resources/controller.py /app/controller.py

RUN pip install kubernetes

CMD ["python", "/app/controller.py"]
