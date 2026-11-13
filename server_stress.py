# server_stress.py - Termux version
# STRESS TEST YOUR OWN SERVER ONLY.
# Do NOT run against servers you don't own / don't have permission to test.

import argparse
import threading
import time
import urllib.request
import urllib.error
import statistics
from collections import Counter

# Shared stats
results = []
results_lock = threading.Lock()
stop_flag = threading.Event()

def worker(url, method, duration, delay, headers, payload):
    end = time.time() + duration
    while not stop_flag.is_set() and time.time() < end:
        start = time.time()
        try:
            req = urllib.request.Request(url, data=payload, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
                status = resp.status
                err = ""
        except urllib.error.HTTPError as e:
            status = e.code
            err = f"HTTP {e.code}"
        except Exception as e:
            status = 0
            err = type(e).__name__

        latency = (time.time() - start) * 1000
        with results_lock:
            results.append((status, latency, err))

        # Rate limit - this is what makes it a test, not a flood
        if delay > 0:
            elapsed = time.time() - start
            sleep_for = delay - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

def main():
    p = argparse.ArgumentParser(description="Termux server stress test for YOUR OWN server")
    p.add_argument("--url", required=True, help="e.g. http://localhost:8000/api/health")
    p.add_argument("--method", default="GET", choices=["GET", "POST"])
    p.add_argument("--threads", type=int, default=10, help="Concurrent threads (max 50)")
    p.add_argument("--duration", type=int, default=20, help="Seconds (max 120)")
    p.add_argument("--rps", type=int, default=50, help="Target total RPS (max 500)")
    p.add_argument("--header", action="append", default=[], help="Header as Key:Value")
    args = p.parse_args()

    # Safety caps for Termux / controlled testing
    if args.threads > 50:
        print("Cap: threads max 50 for Termux test")
        return
    if args.rps > 500:
        print("Cap: rps max 500 for Termux test")
        return
    if args.duration > 120:
        print("Cap: duration max 120s")
        return

    headers = {"User-Agent": "Termux-LoadTester/1.0"}
    for h in args.header:
        if ":" in h:
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()

    # Per-thread delay to hit target RPS
    rps_per_thread = args.rps / args.threads if args.threads else 0
    delay = 1.0 / rps_per_thread if rps_per_thread > 0 else 0

    print(f"Testing {args.url}")
    print(f"Threads={args.threads} Duration={args.duration}s Target RPS={args.rps}")
    print("Only test a server you own. Starting in 3s... Ctrl+C to stop")
    time.sleep(3)

    start_time = time.time()
    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(args.url, args.method, args.duration, delay, headers, None), daemon=True)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nStopped early")
        stop_flag.set()

    elapsed = time.time() - start_time
    total = len(results)
    if total == 0:
        print("No requests completed.")
        return

    latencies = sorted([r[1] for r in results])
    codes = Counter([r[0] for r in results])
    errors = Counter([r[2] for r in results if r[2]])
    success = sum(v for k, v in codes.items() if 200 <= k < 300)

    def pct(p):
        idx = int(len(latencies) * p / 100)
        return latencies[min(idx, len(latencies)-1)]

    print("\n=== STRESS TEST RESULT ===")
    print(f"Total requests: {total}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Actual RPS: {total/elapsed:.2f}")
    print(f"Success (2xx): {success} ({success/total*100:.1f}%)")
    print(f"Status codes: {dict(codes)}")
    print(f"Latency avg: {statistics.mean(latencies):.1f}ms")
    print(f"Latency p50: {pct(50):.1f}ms")
    print(f"Latency p90: {pct(90):.1f}ms")
    print(f"Latency p95: {pct(95):.1f}ms")
    print(f"Latency p99: {pct(99):.1f}ms")
    print(f"Latency max: {latencies[-1]:.1f}ms")
    if errors:
        print(f"Errors: {dict(errors)}")

if __name__ == "__main__":
    main()
