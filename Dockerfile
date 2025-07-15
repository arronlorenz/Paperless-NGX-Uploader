FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies during build for faster startup
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Copy the uploader script into the image
COPY uploader.py ./

ENTRYPOINT ["python", "/app/uploader.py"]
