# GigProof OCR Server

Self-hosted Tesseract OCR HTTP server for GigProof screenshot ingestion.

- **Engine:** Tesseract OCR (Apache 2.0, no API tokens, no per-page fees)
- **API:** FastAPI + Uvicorn, single `POST /ocr` endpoint
- **Docker:** Multi-arch image (amd64 + arm64) for Oracle Cloud Always Free Ampere ARM VM
- **Privacy:** Images never leave your infrastructure

## Quick start (Oracle Cloud Always Free)

1. Create an Always Free Ampere A1 instance (4 OCPUs / 24 GB ARM is the free allowance).
2. SSH in and install Docker:
   ```bash
   sudo yum install -y docker
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
3. Clone this repo and build:
   ```bash
   git clone https://github.com/chetstojanovich-ship-it/gigproof-ocr-server.git
   cd gigproof-ocr-server
   docker build -t gigproof-ocr:latest .
   ```
4. Run:
   ```bash
   docker run -d --name gigproof-ocr --restart unless-stopped -p 8884:8884 gigproof-ocr:latest
   ```
5. Test:
   ```bash
   curl -s http://127.0.0.1:8884/health
   curl -F "file=@screenshot.png" http://127.0.0.1:8884/ocr
   ```

## API

- `GET /health` — liveness check
- `POST /ocr` — multipart form with `file` (image), optional `lang` (default `eng`) and `psm` (default 6)

## Notes

- Default Tesseract PSM 6 is tuned for a block of text, which fits Uber Eats / DeliverThat offer screenshots.
- Add more language packs in the Dockerfile (`tesseract-ocr-data-*`) if you need them.
- Firewall: open port 8884 only to your known IPs.
