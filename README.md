# Raspberry Pi Homelab

Hardware:
- Raspberry Pi 4B
- 2 GB RAM
- 64GB SD Card

Services:
- Grafana Alloy — system monitoring sent to Grafana Cloud
- Pi-hole — network-wide DNS filtering

## Network

- Raspberry Pi hostname: 
- Pi-hole IP: 192.168.0.236

## Repository structure

```text
.
|-- .gitignore         # ignored local files and generated artifacts
|-- LICENSE            # repository license
|-- README.md          # project overview and setup notes
|-- compose.yaml       # shared container orchestration
|-- .env.example       # example environment variables
|-- .env               # local environment variables
|-- services/          # service-specific configs and assets
|   |-- alloy/
|   |   `-- config/
|   |       `-- config.alloy   # current Grafana Alloy configuration
|   `-- <service>/     # future pattern: one folder per service
`-- docs/              # optional extra documentation for larger repos
```

Keep shared files in the repository root, put each service in its own folder under `services/`, and store that service's config files in a dedicated subfolder such as `config/` when needed.
