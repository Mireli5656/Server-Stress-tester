# Server Stress Tester

A lightweight HTTP load testing tool for Termux and any Python environment. It has no external dependencies and uses only the Python standard library.

> **Warning:** Only test servers you **own** or have **explicit written permission** to test. Unauthorized load testing may be illegal.

## Features

- Multi-threaded concurrent requests
- Target requests-per-second (RPS) limiting
- Configurable test duration
- GET and POST support (with custom request body)
- Custom request headers
- Latency statistics: average, p50, p90, p95, p99, max
- Status code and error breakdown
- Built-in safety caps for controlled testing

## Requirements

- Python 3.6+ (uses f-strings)
- No additional `pip` packages required

## Installation

```bash
git clone https://github.com/Mireli5656/Server-Stress-tester
cd Server-Stress-tester
```

For Termux (Android) users:

```bash
pkg install python
```

## Usage

```bash
python server_stress.py --url http://example.com --threads 10 --duration 20 --rps 50
```

With custom headers:

```bash
python server_stress.py --url http://localhost:8000/api/health \
  --header "Authorization: Bearer TOKEN" \
  --header "Accept: application/json"
```

POST with an inline body:

```bash
python server_stress.py --url http://localhost:8000/api \
  --method POST \
  --data '{"name":"test"}'
```

POST with a body read from a file:

```bash
python server_stress.py --url http://localhost:8000/api \
  --method POST \
  --data @body.json
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | *required* | Target URL, e.g. `http://localhost:8000/api/health` |
| `--method` | `GET` | HTTP method (`GET` or `POST`) |
| `--threads` | `10` | Number of concurrent threads (max 50) |
| `--duration` | `20` | Test duration in seconds (max 120) |
| `--rps` | `50` | Target total requests per second (max 500) |
| `--header` | none | Custom header as `Key:Value`. Can be used multiple times |
| `--data` | none | Request body for POST. Use `@file.json` to read it from a file |

## Request Body

- `--data` can only be used together with `--method POST`.
- If you do not set a `Content-Type` header, `application/json` is used by default.
- To send another type, override it with `--header "Content-Type: application/x-www-form-urlencoded"`.

## Safety Limits

To prevent accidental flooding, the tool refuses to run if:

- `--threads` is greater than 50
- `--rps` is greater than 500
- `--duration` is greater than 120 seconds

## Example Output

```
=== STRESS TEST RESULT ===
Total requests: 1000
Duration: 20.05s
Actual RPS: 49.88
Success (2xx): 1000 (100.0%)
Status codes: {200: 1000}
Latency avg: 42.3ms
Latency p50: 38.1ms
Latency p90: 61.7ms
Latency p95: 74.2ms
Latency p99: 112.5ms
Latency max: 180.4ms
```

## Notes

- Press `Ctrl+C` to stop the test early.
- Requests time out after 10 seconds.
- The tool waits 3 seconds before starting, giving you time to cancel.
- Actual RPS may be lower than the target if the server responds slowly.

## License

MIT
