# DockerMonitor

Lightweight Docker container monitoring tool. Collects CPU, memory, and network metrics from all running containers, writes them to CSV, and generates an HTML report with charts grouped by container name prefix.

> **Note**: This is a working prototype built for personal use while working with a multi-container Docker environment. It does the job but is not production-hardened.

---

## What it does

- Polls all running containers every 25 seconds via the Docker SDK
- Collects per-container: CPU %, memory usage/limit (MB), network RX/TX (MB), status
- Writes metrics to `container_stats.csv` continuously
- Generates an HTML report with matplotlib charts — one section per container group
- Containers are grouped by name prefix — configurable via `--prefixes` (default: `backend`, `frontend`, `worker`)
- Can run as a Docker container itself via the included `Dockerfile`

---

## Stack

- **Python 3.12**
- [docker](https://docker-py.readthedocs.io/) — Docker SDK for Python
- [pandas](https://pandas.pydata.org/) — CSV loading for chart generation
- [matplotlib](https://matplotlib.org/) — chart rendering

---

## Installation

```bash
git clone https://github.com/Evil2997/MonitoringSystem.git
cd MonitoringSystem

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### 1. Start monitoring

```bash
python monitor.py
```

Starts polling all running containers and writing to `container_stats.csv`. Stop with `Ctrl+C`.

### 2. Generate HTML report

```bash
# Default groups (backend, frontend, worker)
python plot_from_csv.py

# Custom groups
python plot_from_csv.py --prefixes api worker db --csv my_stats.csv --output report.html
```

Reads the CSV and produces an HTML report with charts for each container group.

### 3. Run as Docker container

```bash
docker build -t docker-monitor .
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/app \
  docker-monitor
```

The container needs access to the Docker socket to query other containers.

---

## Output

**`container_stats.csv`** — raw metrics, appended every 25 seconds:

| Timestamp | Container Name | CPU (%) | Memory Usage (MB) | Memory Usage (%) | Network RX (MB) | Network TX (MB) | Status |
|---|---|---|---|---|---|---|---|

**`monitoring_graphs.html`** — self-contained HTML with embedded charts (no external dependencies):

- CPU usage over time
- Memory usage over time
- Network RX/TX over time

Each container group gets its own section.

---

## Known limitations

- Container grouping is configurable via `--prefixes` CLI argument (default: `backend`, `frontend`, `worker`) — containers not matching any prefix go into the `other` group
- `monitor_control.py` is an unfinished experiment and is not functional in the current version
- CSV is not flushed between iterations — data may be lost if the process crashes
- Poll interval is hardcoded at 25 seconds

---

## Origin

Built as a personal monitoring utility while working with a multi-container production environment. The goal was a simple, dependency-light way to observe resource trends over time and generate a sharable HTML snapshot — without setting up Prometheus or Grafana for a small project.