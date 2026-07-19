# Homelab Documentation

The homelab runs from `/opt/homelab` on a Raspberry Pi using one shared Docker Compose project.

## Addition 1: Git, Docker, Alloy, and Grafana Cloud

1. Install Git and Docker Engine with the Docker Compose plugin.
2. Add the current user to the `docker` group, then sign out and back in:

   ```sh
   sudo usermod -aG docker "$USER"
   ```

3. Clone this repository into `/opt/homelab`.
4. Copy `.env.example` to `.env` and enter the Grafana Cloud Prometheus URL, instance ID, access-policy token, and Alloy hostname.
5. Start Alloy:

   ```sh
   docker compose up -d alloy
   docker compose logs -f alloy
   ```

Alloy collects Raspberry Pi system metrics from the mounted host filesystems and sends them to Grafana Cloud. Its local interface listens only on `127.0.0.1:12345`.

## Addition 2: Pi-hole

1. Set `PIHOLE_WEBPASSWORD` in `.env`.
2. Ensure the Raspberry Pi has a static IP or a DHCP reservation.
3. Start Pi-hole:

   ```sh
   docker compose up -d pihole
   docker compose logs -f pihole
   ```

4. Open `http://192.168.0.236:8080/admin` and sign in.
5. Configure the router's LAN DNS server to `192.168.0.236`.

Pi-hole stores its persistent data in `services/pihole/etc-pihole/`. These generated files are excluded from Git.

## Common operations

Run commands from `/opt/homelab`:

```sh
# Start or apply configuration changes
docker compose up -d

# Check service state
docker compose ps

# Follow logs
docker compose logs -f alloy
docker compose logs -f pihole

# Pull newer images and recreate the containers
docker compose pull
docker compose up -d

# Stop the stack without deleting persistent data
docker compose down
```

Back up `.env` securely and copy `services/pihole/etc-pihole/` before major Pi-hole changes. Do not commit `.env`, tokens, passwords, or generated Pi-hole data.

## Common issues

### Permission denied in `/opt/homelab`

The directory may be owned by `root`, preventing the current user from updating the repository or writing persistent files.

```sh
sudo chown -R "$USER":"$USER" /opt/homelab
```

### Permission denied when running Docker

Add the user to the `docker` group, then sign out and back in:

```sh
sudo usermod -aG docker "$USER"
```

Use `groups` to confirm that the new session includes the `docker` group.

### Port 53 is already in use

Find the process using DNS port 53:

```sh
sudo ss -lntup | grep ':53 '
```

Disable or reconfigure the conflicting DNS service before starting Pi-hole. On systems using `systemd-resolved`, confirm its role before changing it because incorrect DNS settings can disconnect the host from name resolution.

### Required environment variable is missing

Create `.env` from the example and fill in every required value:

```sh
test -f .env || cp .env.example .env
docker compose config
```

### DNS works locally but not for other devices

Confirm that the router advertises `192.168.0.236` as its LAN DNS server, clients have renewed their DHCP leases, and TCP/UDP port 53 is not blocked by the host firewall.

### Grafana Cloud receives no metrics

Check the Alloy logs and verify the metrics URL, instance ID, token, and `metrics:write` permission in `.env`. After changing `.env`, recreate Alloy with `docker compose up -d alloy`.
