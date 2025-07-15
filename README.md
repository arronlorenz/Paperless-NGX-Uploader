# Paperless-NGX-Uploader

Helper container to upload PDFs to Paperless-NGX using its REST API.

## Environment variables

| Variable | Purpose |
|----------|--------------------------------------------------------------------------|
| `PAPERLESS_URL` | Base URL of your Paperless-NGX instance, e.g. `http://paperless.lan:8000` |
| `PAPERLESS_TOKEN` | API token created in Paperless. Required. |
| `SOURCE_DIRS` | Semicolon separated list of directories to scan for `*.pdf`. |
| `STATE_DB` | Path to the SQLite database that tracks uploaded files and their hashes. |
| `MIN_AGE` | Seconds to wait after file modification time before upload (default `60`). |
| `SCAN_INTERVAL` | Seconds between directory scans (default `300`). |
| `TZ` | Optional timezone for logs. |

## Build

```bash
docker build -t paperless-api-uploader .
```

## Run

```bash
docker run \
  -e PAPERLESS_URL=http://paperless.lan:8000 \
  -e PAPERLESS_TOKEN=YOURTOKEN \
  -e SOURCE_DIRS="/nas/sharepoint;/nas/p21sftp" \
  -v /volume1/doclinks/sharepoint:/nas/sharepoint:ro \
  -v /volume1/doclinks/p21sftp:/nas/p21sftp:ro \
  -v /volume1/doclinks/apiuploader:/state \
  paperless-api-uploader
```

## Example output

```
[OK] /nas/sharepoint/Invoice_123.pdf
[OK] /nas/p21sftp/PO_456.pdf
```
Each file is uploaded once; later scans skip it silently.
The uploader also stores a SHA-256 hash for each document in the state
database so that modified files are re-uploaded even if their size and
timestamp are unchanged.

## Adding metadata fields

The Paperless API accepts extra form data such as `title`, `document_type` or
`tags`. Add them in the `requests.post()` call inside `uploader.py` as shown
below (lines 31‑40 of the original README):

```python
r = requests.post(
    URL, headers=headers,
    files={"document": (pdf.name, fp, "application/pdf")},
    data={"document_type": 7, "tags": [16, 42]}
)
```

## Deploy steps in Synology Container Manager

1. Create `/doclinks/apiuploader` in File Station to hold the upload state database.
2. In Container Manager → Projects → Create, paste the contents of `compose.yaml`.
3. Replace `PAPERLESS_URL` and `PAPERLESS_TOKEN` with your values.
4. Click **Next** → **Deploy** and monitor the logs.
