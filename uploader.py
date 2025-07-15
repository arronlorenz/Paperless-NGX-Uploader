import os, time, pathlib, sqlite3, requests, sys

URL   = os.getenv("PAPERLESS_URL").rstrip("/") + "/api/documents/post_document/"
TOKEN = os.getenv("PAPERLESS_TOKEN")
MIN   = int(os.getenv("MIN_AGE", "60"))
STEP  = int(os.getenv("SCAN_INTERVAL", "300"))
DB    = os.getenv("STATE_DB", "/state/uploaded.db")
DIRS  = os.getenv("SOURCE_DIRS", "").split(";")

con = sqlite3.connect(DB)
con.execute("CREATE TABLE IF NOT EXISTS done(path TEXT PRIMARY KEY, m REAL, s INTEGER)")

headers = {"Authorization": f"Token {TOKEN}"}

while True:
    cur = con.cursor()
    for root in DIRS:
        for pdf in pathlib.Path(root).rglob("*.pdf"):
            st = pdf.stat()
            if time.time() - st.st_mtime < MIN:
                continue                                # file still being written
            cur.execute("SELECT 1 FROM done WHERE path=? AND m=? AND s=?",
                        (str(pdf), st.st_mtime, st.st_size))
            if cur.fetchone():
                continue                                # already uploaded

            try:
                with pdf.open("rb") as fp:
                    r = requests.post(
                        URL,
                        headers=headers,
                        files={"document": (pdf.name, fp, "application/pdf")},
                    )
                r.raise_for_status()
                cur.execute("INSERT INTO done VALUES(?,?,?)",
                            (str(pdf), st.st_mtime, st.st_size))
                con.commit()
                print(f"[OK] {pdf}")
            except Exception as e:
                print(f"[FAIL] {pdf}: {e}", file=sys.stderr)
    time.sleep(STEP)
