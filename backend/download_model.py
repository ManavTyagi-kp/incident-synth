import os, sys, time
from google.cloud import storage

def log(msg):
    print(msg, flush=True)

BUCKET = os.environ["MODEL_BUCKET"]
BLOB = os.environ["MODEL_BLOB"]
DEST = "/app/models/incident-slm.gguf"

def main():
    if os.path.exists(DEST):
        log(f"Model already present at {DEST}, skipping download.")
        return
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    log(f"Starting download: gs://{BUCKET}/{BLOB} -> {DEST}")
    start = time.time()
    try:
        client = storage.Client()
        log("Storage client created.")
        bucket = client.bucket(BUCKET)
        blob = bucket.blob(BLOB)
        log("Fetching blob metadata...")
        blob.reload(timeout=30)
        log(f"Blob size on server: {blob.size} bytes")
        blob.download_to_filename(DEST, timeout=180)
        elapsed = time.time() - start
        log(f"Download complete in {elapsed:.1f}s, local size: {os.path.getsize(DEST)} bytes")
    except Exception:
        import traceback
        log("DOWNLOAD ERROR:")
        log(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
