# 🚀 Async API Load Testing Tool (Python)

A lightweight asynchronous load testing tool built using Python `asyncio` and `aiohttp`.

## Features
- Async concurrent API requests
- Token-based authentication support
- Latency tracking (Avg, P50, P90, P95, P99)
- Throughput (Requests per second)
- CSV export of results
- CLI-based configuration

## Tech Stack
- Python 3.10+
- aiohttp
- asyncio

## How to Run

```bash
pip install aiohttp
python load_test.py --requests 25 --concurrency 100
