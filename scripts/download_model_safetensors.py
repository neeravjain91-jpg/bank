import os
import sys
import time
import urllib.request
import concurrent.futures
from pathlib import Path

TARGET_URL = "https://huggingface.co/typeform/distilbert-base-uncased-mnli/resolve/main/model.safetensors"
EXPECTED_SIZE = 267835640  # Exact Content-Length

SNAPSHOT_DIR = Path(r"C:\Users\ASUS\.cache\huggingface\hub\models--typeform--distilbert-base-uncased-mnli\snapshots\cfa538a0fddbbd978fefe8966c1aeff7ad409c90")
TARGET_FILE = SNAPSHOT_DIR / "model.safetensors"
PART_FILE = SNAPSHOT_DIR / "model.safetensors.part"

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB per chunk
NUM_WORKERS = 8

def download_chunk(chunk_idx, start_byte, end_byte):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Range": f"bytes={start_byte}-{end_byte}"
    }
    req = urllib.request.Request(TARGET_URL, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                expected_len = end_byte - start_byte + 1
                if len(data) != expected_len:
                    raise IOError(f"Chunk {chunk_idx}: expected {expected_len} bytes, got {len(data)}")
                return chunk_idx, start_byte, data
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(1 + attempt)

def main():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    if TARGET_FILE.exists() and TARGET_FILE.stat().st_size == EXPECTED_SIZE:
        print(f"model.safetensors already completely downloaded ({EXPECTED_SIZE} bytes).")
        return

    print("=" * 80)
    print("PARALLEL DOWNLOADER: typeform/distilbert-base-uncased-mnli (model.safetensors)")
    print(f"Target size: {EXPECTED_SIZE / (1024*1024):.2f} MB | Workers: {NUM_WORKERS} | Chunk: {CHUNK_SIZE/(1024*1024):.1f} MB")
    print("=" * 80)

    # Pre-allocate sparse/zero-filled part file
    with open(PART_FILE, "wb") as fp:
        fp.seek(EXPECTED_SIZE - 1)
        fp.write(b"\0")

    chunks = []
    idx = 0
    curr = 0
    while curr < EXPECTED_SIZE:
        end = min(curr + CHUNK_SIZE - 1, EXPECTED_SIZE - 1)
        chunks.append((idx, curr, end))
        idx += 1
        curr = end + 1

    total_chunks = len(chunks)
    completed_bytes = 0
    t0 = time.time()
    last_log = t0

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(download_chunk, c[0], c[1], c[2]): c for c in chunks}
        
        with open(PART_FILE, "r+b") as out_fp:
            for fut in concurrent.futures.as_completed(futures):
                chunk_idx, start_byte, data = fut.result()
                out_fp.seek(start_byte)
                out_fp.write(data)
                completed_bytes += len(data)
                
                now = time.time()
                if now - last_log >= 5.0 or completed_bytes == EXPECTED_SIZE:
                    elapsed = now - t0
                    speed = (completed_bytes / (1024 * 1024)) / (elapsed + 1e-6)
                    pct = (completed_bytes / EXPECTED_SIZE) * 100
                    rem_bytes = EXPECTED_SIZE - completed_bytes
                    eta = (rem_bytes / (speed * 1024 * 1024)) if speed > 0 else 0
                    print(f"[{pct:5.1f}%] {completed_bytes / (1024*1024):.1f}/{EXPECTED_SIZE / (1024*1024):.1f} MB "
                          f"| Speed: {speed:.2f} MB/s | Elapsed: {elapsed:.0f}s | ETA: {eta:.0f}s")
                    last_log = now

    if PART_FILE.stat().st_size != EXPECTED_SIZE:
        raise ValueError(f"Downloaded file size mismatch: {PART_FILE.stat().st_size} vs {EXPECTED_SIZE}")

    if TARGET_FILE.exists():
        TARGET_FILE.unlink()
    PART_FILE.rename(TARGET_FILE)

    total_time = time.time() - t0
    avg_speed = (EXPECTED_SIZE / (1024 * 1024)) / total_time
    print("=" * 80)
    print(f"DOWNLOAD COMPLETE: {TARGET_FILE}")
    print(f"Total time: {total_time:.1f}s | Avg Speed: {avg_speed:.2f} MB/s | Size: {EXPECTED_SIZE} bytes")
    print("=" * 80)

if __name__ == "__main__":
    main()
