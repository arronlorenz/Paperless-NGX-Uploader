import os, time, pathlib, sqlite3, requests, sys, hashlib

url_env   = os.getenv("PAPERLESS_URL")
token_env = os.getenv("PAPERLESS_TOKEN")
missing = [name for name, val in (("PAPERLESS_URL", url_env), ("PAPERLESS_TOKEN", token_env)) if not val]
if missing:
    print(f"Error: Missing required environment variable(s): {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

URL   = url_env.rstrip("/") + "/api/documents/post_document/"
TOKEN = token_env
MIN   = int(os.getenv("MIN_AGE", "60"))
STEP  = int(os.getenv("SCAN_INTERVAL", "300"))
DB    = os.getenv("STATE_DB", "/state/uploaded.db")
DIRS  = os.getenv("SOURCE_DIRS", "").split(";")

con = sqlite3.connect(DB)
con.execute(
    "CREATE TABLE IF NOT EXISTS done(path TEXT PRIMARY KEY, m REAL, s INTEGER, h TEXT)"
)

# Add hash column if database was created by an older version
cols = [row[1] for row in con.execute("PRAGMA table_info(done)")] 
if "h" not in cols:
    con.execute("ALTER TABLE done ADD COLUMN h TEXT")

headers = {"Authorization": f"Token {TOKEN}"}

def file_sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


while True:
    cur = con.cursor()
    for root in DIRS:
        for pdf in pathlib.Path(root).rglob("*.pdf"):
            st = pdf.stat()
            if time.time() - st.st_mtime < MIN:
                continue                                # file still being written

            sha = file_sha256(pdf)
            cur.execute(
                "SELECT 1 FROM done WHERE path=? AND m=? AND s=? AND h=?",
                (str(pdf), st.st_mtime, st.st_size, sha),
            )
            if cur.fetchone():
                continue                                # already uploaded

            try:
                with pdf.open("rb") as fp:
                    r = requests.post(
                        URL,
                        headers=headers,
                        files={"document": (pdf.name, fp, "application/pdf")},
                        timeout=30,
                    )
                r.raise_for_status()
                cur.execute(
                    "INSERT OR REPLACE INTO done VALUES(?,?,?,?)",
                    (str(pdf), st.st_mtime, st.st_size, sha),
                )
                con.commit()
                print(f"[OK] {pdf}")
            except Exception as e:
                print(f"[FAIL] {pdf}: {e}", file=sys.stderr)
    time.sleep(STEP)
