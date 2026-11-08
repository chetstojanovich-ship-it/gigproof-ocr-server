FROM --platform=$TARGETPLATFORM alpine:3.20

ARG TARGETARCH

RUN apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app.py .

EXPOSE 8884

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8884/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8884"]