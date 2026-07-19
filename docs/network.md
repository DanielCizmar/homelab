# Network

## Host

- Device: Raspberry Pi 4B
- Pi-hole and Raspberry Pi IP: `192.168.0.236`
- Hostname: not yet documented
- Time zone: `Europe/Bratislava`

Keep `192.168.0.236` stable with a router DHCP reservation or a correctly configured static address. If this address changes, clients will lose DNS resolution.

## DNS flow

```text
LAN client
  -> Raspberry Pi / Pi-hole (192.168.0.236:53)
  -> Cloudflare DNS (1.1.1.1 or 1.0.0.1)
```

Configure the router's LAN DHCP settings to advertise `192.168.0.236` as the DNS server. Renew client DHCP leases after making the change. Avoid advertising a public secondary DNS server to clients because they may bypass Pi-hole.

## Exposed services

| Service | Port | Protocol | Access |
| --- | ---: | --- | --- |
| Pi-hole DNS | 53 | TCP/UDP | LAN |
| Pi-hole dashboard | 8080 | TCP/HTTP | `http://192.168.0.236:8080/admin` |
| Pi-hole dashboard | 8443 | TCP/HTTPS | `https://192.168.0.236:8443/admin` |
| Alloy interface | 12345 | TCP/HTTP | Host only (`127.0.0.1`) |

Ports 80 and 443 remain available on the Raspberry Pi for future services.

## Docker networks

- `homelab_dns` isolates the Pi-hole container while published ports provide LAN access.
- `homelab_monitoring` contains Alloy.
- Alloy sends metrics outbound to Grafana Cloud over HTTPS.

The Docker networks are internal implementation details; LAN devices should always use the Raspberry Pi address, not container IP addresses.

## Checks

From another LAN device:

```sh
nslookup example.com 192.168.0.236
```

On the Raspberry Pi:

```sh
docker compose ps
sudo ss -lntup | grep -E ':(53|8080|8443|12345) '
```

Do not expose the Pi-hole dashboard, DNS port, or Alloy interface directly to the public internet.
