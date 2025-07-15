# Paperless-NGX-Uploader
Helper container to upload docs and pdfs to Paperless-NGX via API.


4 Deploy steps in Synology Container Manager
File Station → Shared Folder

Create /doclinks/apiuploader.

Drop uploader.py inside it.

Container Manager → Projects → Create

Paste the YAML above.

Replace PAPERLESS_URL and PAPERLESS_TOKEN.

Click Next → Deploy.

Watch the logs
Container Manager → Containers → paperless-api-uploader → Logs.
You should see lines like

bash
Copy
Edit
[OK] /nas/sharepoint/Invoice_123.pdf
[OK] /nas/p21sftp/PO_456.pdf
Each file is uploaded once; later scans skip it silently.

5 Need tags or metadata?
The Paperless API lets you pass extra form fields (title=, document_type=, tags=…).
Add them in the requests.post() call inside uploader.py, e.g.:

python
Copy
Edit
r = requests.post(
    URL, headers=headers,
    files={"document": (pdf.name, fp, "application/pdf")},
    data={"document_type": 7, "tags": [16, 42]}
)
