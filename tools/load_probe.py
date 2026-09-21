"""Bounded HTTP load probe; remote targets require explicit opt-in."""
import argparse
import concurrent.futures
import json
import os
import statistics
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.core.load_safety import assert_safe_target


def request(base_url: str, path: str, token: str | None) -> dict:
    started = time.perf_counter()
    try:
        response = httpx.get(base_url.rstrip('/') + path, headers={'Authorization': f'Bearer {token}'} if token else {}, timeout=10)
        return {'status': response.status_code, 'latency_ms': round((time.perf_counter() - started) * 1000, 2)}
    except httpx.HTTPError as exc:
        return {'status': 0, 'latency_ms': round((time.perf_counter() - started) * 1000, 2), 'error': type(exc).__name__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://localhost:8000')
    parser.add_argument('--path', default='/ready')
    parser.add_argument('--requests', type=int, default=25)
    parser.add_argument('--concurrency', type=int, default=5)
    parser.add_argument('--allow-remote', action='store_true')
    parser.add_argument('--output', default='reports/load/latest.json')
    args = parser.parse_args()
    assert_safe_target(args.base_url, args.allow_remote)
    if args.requests < 1 or args.concurrency < 1:
        parser.error('requests and concurrency must be positive')
    token = os.getenv('LOADTEST_BEARER_TOKEN')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        results = list(pool.map(lambda _: request(args.base_url, args.path, token), range(args.requests)))
    latency = sorted(row['latency_ms'] for row in results)
    at = lambda p: latency[min(len(latency) - 1, max(0, int(len(latency) * p + 0.999) - 1))]
    report = {'target': args.base_url, 'path': args.path, 'configuration': {'requests': args.requests, 'concurrency': args.concurrency}, 'summary': {'requests': len(results), 'success_rate': round(sum(200 <= item['status'] < 400 for item in results) / len(results), 4), 'p50_ms': at(.5), 'p95_ms': at(.95), 'p99_ms': at(.99), 'max_ms': max(latency)}}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
