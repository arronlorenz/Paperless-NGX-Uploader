FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm -rf /root/.cache/pip
ENTRYPOINT ["python", "/app/uploader.py"]
