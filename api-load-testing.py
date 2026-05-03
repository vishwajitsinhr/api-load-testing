import asyncio
import aiohttp
import getpass
import time
import statistics
import csv
import argparse

# --- API Endpoints (placeholders) ---
TOKEN_URL = "https://api.example.com/token"
FEED_URLS = {
    "Feed_1": "https://api.example.com/feed1?token={token}",
    "Feed_2": "https://api.example.com/feed2?token={token}",
    "Feed_3": "https://api.example.com/feed3?token={token}",
}

# --- Stats storage ---
results = []

async def get_token(session, username, password):
    payload = {"username": username, "password": password}
    headers = {"Accept": "application/json"}
    async with session.post(TOKEN_URL, json=payload, headers=headers) as resp:
        data = await resp.json()
        return data.get("Entity", {}).get("Token")

async def load_test_feed(session, feed_name, url, token, sem):
    url = url.format(token=token)
    async with sem:
        start = time.perf_counter()
        try:
            async with session.get(url, headers={"Accept": "application/xml"}) as resp:
                await resp.read()
                duration = time.perf_counter() - start
                results.append((feed_name, resp.status, duration))
                print(f"✅ {feed_name} [{resp.status}] in {duration:.2f}s")
        except Exception as e:
            duration = time.perf_counter() - start
            results.append((feed_name, 'ERROR', duration))
            print(f"❌ {feed_name} [ERROR] in {duration:.2f}s: {e}")

def summarize_results():
    print("\n📊 Load Test Summary:")
    for feed in FEED_URLS:
        durations = [d for n, s, d in results if n == feed and s == 200]
        errors = len([1 for n, s, _ in results if n == feed and s != 200])
        total = len(durations) + errors

        if durations:
            avg = statistics.mean(durations)
            p50 = statistics.median(durations)
            p90 = statistics.quantiles(durations, n=100)[89]  # 90th percentile
            p95 = statistics.quantiles(durations, n=100)[94]  # 95th percentile
            p99 = statistics.quantiles(durations, n=100)[98]  # 99th percentile
            rps = len(durations) / sum(durations)

            print(f"\n🔹 {feed}:")
            print(f"   ✔ {len(durations)}/{total} ok, {errors} errors")
            print(f"   ⏱ Avg={avg:.2f}s | P50={p50:.2f}s | P90={p90:.2f}s | P95={p95:.2f}s | P99={p99:.2f}s")
            print(f"   ⚡ Throughput: {rps:.2f} req/sec")
        else:
            print(f"\n🔹 {feed}: all failed.")

def export_csv(filename="load_test_results.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Feed", "Status", "Duration(s)"])
        writer.writerows(results)
    print(f"\n📁 Results exported to {filename}")

async def main(requests_per_feed, concurrency):
    username = input("👤 Username: ")
    password = getpass.getpass("🔒 Password: ")
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        token = await get_token(session, username, password)
        print(f"\n🔑 Token received: {token[:10]}...\n")

        tasks = [
            load_test_feed(session, name, url, token, sem)
            for _ in range(requests_per_feed)
            for name, url in FEED_URLS.items()
        ]

        start_time = time.perf_counter()
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    summarize_results()
    print(f"\n⏳ Total test duration: {total_time:.2f}s")
    export_csv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async API Load Tester")
    parser.add_argument("--requests", type=int, default=25, help="Requests per feed (default=25)")
    parser.add_argument("--concurrency", type=int, default=100, help="Max concurrent requests (default=100)")
    args = parser.parse_args()

    asyncio.run(main(args.requests, args.concurrency))