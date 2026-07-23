# Tailscale documentation

Check if Tailscale is installed and version: 

tailscale version

Check if Tailscale service is running:

sudo systemctl status tailscaled

Connect Pi to Tailscale network:

sudo tailscale up

Check connection and IPv4:

tailscale status

To connect to Raspberry Pi from a computer from different network install Tailscale app on your computer and connect via Tailscale IP. Example:

ssh piadmin@100.x.x.x

