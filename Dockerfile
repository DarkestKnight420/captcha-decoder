FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y libopencv-dev tesseract-ocr libtesseract-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn python-multipart opencv-python-headless pytesseract

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
