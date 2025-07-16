# Paperless‑NGX Uploader

A lightweight side‑car container that scans local folders for new **PDF** files and pushes them to your Paperless‑NGX instance via its REST API. Ideal for automating uploads from network shares, scanners, or third‑party workflows.

## Highlights

- **Duplicate‑safe** – keeps an SQLite catalog of SHA‑256 hashes so each document is uploaded once, but changed files are detected and re‑sent.
- **Non‑blocking** – files are only processed after they have stopped changing for `MIN_AGE` seconds.
- **Tiny footprint** – built on Python 3 Alpine, under 30 MB.
- **Zero config on Paperless** – uses the official API; no mount of the consume folder required.

## Requirements

| Item          | Notes                                                                  |
| ------------- | ---------------------------------------------------------------------- |
| Paperless‑NGX | v2.5 or newer with the API enabled                                     |
| API Token     | Create in **Settings → API tokens** and copy the value                 |
| PDFs          | The uploader ignores every file that is not `*.pdf` (case‑insensitive) |

## Configuration

All settings are supplied as environment variables.

| Variable          | Default              | Description                                                                                   |
| ----------------- | -------------------- | --------------------------------------------------------------------------------------------- |
| `PAPERLESS_URL`   | –                    | **Required.** Base URL of Paperless, e.g. `http://paperless.lan:8000`.                        |
| `PAPERLESS_TOKEN` | –                    | **Required.** Personal API token created in Paperless.                                        |
| `SOURCE_DIRS`     | –                    | **Required.** Semicolon‑separated list of absolute paths to watch (recursively) for new PDFs. |
| `STATE_DB`        | `/state/uploader.db` | Path to the local SQLite database used for deduplication.                                     |
| `MIN_AGE`         | `60`                 | Seconds to wait after the last modification before a file is considered stable.               |
| `SCAN_INTERVAL`   | `300`                | Seconds between directory walks.                                                              |
| `TZ`              | Container default    | Time‑zone for timestamped log messages.                                                       |

## Quick Start

### 1 — Build & run manually

```bash
docker build -t paperless-uploader .

docker run -d --name uploader \
  -e PAPERLESS_URL=http://paperless.lan:8000 \
  -e PAPERLESS_TOKEN=<TOKEN> \
  -e SOURCE_DIRS="/nas/sharepoint;/nas/p21sftp" \
  -v /volume1/doclinks/sharepoint:/nas/sharepoint:ro \
  -v /volume1/doclinks/p21sftp:/nas/p21sftp:ro \
  -v /volume1/doclinks/apiuploader:/state \
  paperless-uploader
```

### 2 — Docker Compose (recommended)

```yaml
services:
  uploader:
    build: .
    image: paperless-uploader:latest
    restart: unless-stopped
    environment:
      PAPERLESS_URL: http://paperless.lan:8000
      PAPERLESS_TOKEN: ${PAPERLESS_TOKEN}
      SOURCE_DIRS: /nas/sharepoint;/nas/p21sftp
      # optional tweaks:
      # MIN_AGE: "120"
      # SCAN_INTERVAL: "600"
    volumes:
      - /volume1/doclinks/sharepoint:/nas/sharepoint:ro
      - /volume1/doclinks/p21sftp:/nas/p21sftp:ro
      - /volume1/doclinks/apiuploader:/state
```

### 3 — Synology Container Manager

1. Create an empty folder (e.g. `/doclinks/apiuploader`) that the container can write to.
2. Upload this repository (containing `compose.yaml` and `Dockerfile`) to your NAS.
3. *Container Manager → Projects → Create* and select the `compose.yaml`.
4. Fill in `PAPERLESS_URL` and `PAPERLESS_TOKEN`, tweak mount paths if needed.
5. Hit **Next → Deploy**. The first launch builds the image; later launches reuse it.

## Sample Log

```
[2025-07-15 19:02:01] INFO  uploader: Scanned 2 directories, found 0 new PDFs.
[2025-07-15 19:05:22] INFO  uploader: Uploading /nas/sharepoint/Invoice_123.pdf … OK (id=8742)
```

## Adding metadata

Paperless accepts additional form fields such as `title`, `document_type` and `tags`.\
Edit `uploader.py` inside the project:

```python
files = {"document": (pdf.name, fp, "application/pdf")}
data  = {"title": pdf.stem,
         "document_type": 7,
         "tags": [16, 42]}

requests.post(PAPERLESS_URL + "/api/documents/", headers=headers,
              files=files, data=data, timeout=30)
```

## License

MIT — see `LICENSE` for details. Contributions are welcome!

