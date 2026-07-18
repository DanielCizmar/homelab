# Raspberry Pi Homelab

Configuration and documentation for my Raspberry Pi 4b 2GB Homelab.

## Planned services

[x] Git (version control)
[x] Docker
[x] Grafana Alloy (monitoring)
[ ] Pi-Hole (open-source adblock)
[ ] Website hosting
[ ] VPN
[ ] More...

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
