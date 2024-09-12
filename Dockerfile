FROM python:3.12-slim
RUN pip install docker
COPY monitor.py /app/monitor.py
WORKDIR /app
CMD ["python", "monitor.py"]
