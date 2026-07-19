# Pi-hole

## Purpose

Provides network-wide DNS filtering and a web dashboard for managing blocklists and reviewing DNS queries.

## Deployment

Pi-hole runs as the `pihole` service in the root [`compose.yaml`](../../compose.yaml). It exposes DNS on TCP/UDP port `53` and the dashboard at `http://<raspberry-pi-ip>:8080/admin`.

Set `PIHOLE_WEBPASSWORD` in the root `.env` file before starting it. Configure your router or clients to use the Raspberry Pi's static IP as their DNS server.

## Important files

- [`../../compose.yaml`](../../compose.yaml) — image, ports, DNS settings, and volume configuration.
- [`etc-pihole/`](etc-pihole/) — persistent Pi-hole configuration and database files; its contents are intentionally ignored by Git.
- [`../../.env.example`](../../.env.example) — example environment variables.

## Start

Run from the repository root:

```sh
docker compose up -d pihole
docker compose logs -f pihole
```
