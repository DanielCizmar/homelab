# Grafana Alloy

## Purpose

Collects Raspberry Pi system metrics and sends them to Grafana Cloud Prometheus.

## Deployment

Alloy runs as the `alloy` service in the root [`compose.yaml`](../../compose.yaml). It reads host metrics from mounted `/proc`, `/sys`, and root filesystems. Its local UI is available only on the Raspberry Pi at `http://127.0.0.1:12345`.

Copy the root `.env.example` to `.env` and set the Grafana Cloud metrics URL, instance ID, access token, and `ALLOY_HOSTNAME`.

## Important files

- [`config/config.alloy`](config/config.alloy) — metric collection, labels, and remote-write configuration.
- [`../../compose.yaml`](../../compose.yaml) — container, mounts, networking, and persistent storage.
- [`../../.env.example`](../../.env.example) — required environment variables.
- `homelab_alloy-data` — Docker volume containing Alloy's local state.

## Start

Run from the repository root:

```sh
docker compose up -d alloy
docker compose logs -f alloy
```
