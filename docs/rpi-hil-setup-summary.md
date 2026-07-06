# RPi HIL Runner Setup & Platform Control Board Flashing

## Overview

The Raspberry Pi 4 acts as a HIL (Hardware-in-the-Loop) runner. It connects to the
Platform Control Board (STM32H745BITx) via STLINK-V3SET over SWD and flashes firmware
using OpenOCD.

---

## 1. Flash the SD Card (Raspberry Pi Imager v2.0.7)

Use Raspberry Pi Imager with the following customisation:

| Setting | Value |
|---|---|
| Hostname | `hil-runner` |
| Username | `hil` |
| Password | *(set a password you'll remember)* |
| Wi-Fi SSID | *(your office/home Wi-Fi name)* |
| Wi-Fi Password | *(your Wi-Fi password)* |
| SSH | Enable — Use password authentication |

> **Note:** Flash a new SD card whenever switching Wi-Fi networks (home ↔ office)
> until a static IP is configured via router DHCP reservation.

---

## 2. First Boot & SSH

Insert SD card, power on Pi (USB-C, 5V/3A). Wait ~60 seconds.

Find the Pi on the network (from Windows PowerShell):
```powershell
ping hil-runner.local
ssh hil@hil-runner.local
```

If `hil-runner.local` doesn't resolve, find the IP by MAC address:
```powershell
1..254 | ForEach-Object { ping -n 1 -w 100 10.14.34.$_ | Out-Null }
Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.LinkLayerAddress -like "2C-CF-67*" }
```
Pi MAC address: `2C:CF:67:99:3A:6F`

> **Note:** After reflashing, clear the stale SSH host key first:
> ```powershell
> ssh-keygen -R hil-runner.local
> ```

---

## 3. raspi-config

```bash
sudo raspi-config
```

| Menu | Option | Action |
|---|---|---|
| Interface Options | SPI | Enable |
| Interface Options | SSH | Enable (confirm on) |
| Advanced Options | Expand Filesystem | Select |

Reboot when prompted. Reconnect via SSH.

---

## 4. Static IP (Recommended — via Router)

The most reliable method is a **DHCP reservation on the router** (assign a fixed IP
to the Pi's MAC `2C:CF:67:99:3A:6F`). This requires router admin access.

**Do not** use `dhcpcd.conf` — Raspberry Pi OS Bookworm uses NetworkManager.

If router access is available, set reservation to e.g. `10.14.34.50`, then SSH with:
```bash
ssh hil@10.14.34.50
```

**Alternative (NetworkManager method):**
```bash
sudo nmcli con show   # find the connection name
sudo nmcli con mod "netplan-wlan0-<SSID>" ipv4.addresses 10.14.34.50/24 \
    ipv4.gateway 10.14.34.1 ipv4.dns "8.8.8.8" ipv4.method manual
sudo nmcli con up "netplan-wlan0-<SSID>"
```
> ⚠️ Check `ip route | grep default` first to confirm the correct gateway IP.

---

## 5. System Updates & Dependencies

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y can-utils openocd python3-pip python3-venv git binutils-arm-none-eabi
```

Verify:
```bash
openocd --version   # should show 0.12.x
python3 --version
git --version
```

---

## 6. STLINK USB Permissions (udev rules)

Without this, OpenOCD fails with `LIBUSB_ERROR_ACCESS`.

```bash
sudo cp /usr/lib/udev/rules.d/60-openocd.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug the STLINK-V3SET, then verify:
```bash
lsusb | grep STMicro
# Expected: Bus 00X Device 00X: ID 0483:374f STMicroelectronics STLINK-V3
```

---

## 7. Clone Repo & Install Python Dependencies

Generate SSH key for GitHub deploy key access:
```bash
ssh-keygen -t ed25519 -C "hil-runner"
cat ~/.ssh/id_ed25519.pub
```

Add the printed key to: **GitHub → repo → Settings → Deploy keys → Add deploy key**

Test connection:
```bash
ssh -T git@github.com
```

Clone and set up:
```bash
git clone git@github.com:<org>/automated-test.git
cd automated-test
python3 -m venv .venv
source .venv/bin/activate
pip install -r hil/requirements.txt
```

---

## 8. Flash Platform Control Board

```bash
cd ~/automated-test
source .venv/bin/activate
./scripts/flash_firmware.sh \
    boards/firmwares/platform-control-board/ControlBrd1_CM7.elf \
    boards/firmwares/platform-control-board/ControlBrd1_CM4.elf
```

Expected output (success):
```
INFO Stripped ControlBrd1_CM7.elf: 30157 KB → 2484 KB
INFO Stripped ControlBrd1_CM4.elf: 2165 KB → 50 KB
** Programming Finished **   ← CM7
** Programming Finished **   ← CM4
INFO Flash completed in ~22s (exit code 0)
```

> **Known non-errors (safe to ignore):**
> - `STM32H745BITx.cpu1 cannot read the flash size register` — OpenOCD 0.12 quirk with CM4
> - `cpu1 clearing lockup after double fault` — CM4 starts before CM7 releases it; expected on STM32H745

---

## 9. SocketCAN Setup (Canable 2.0) — Pending hardware arrival

```bash
sudo modprobe can
sudo modprobe can_raw
sudo modprobe can_dev
sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on sample-point 0.75
ip -details link show can0
candump can0
```

Make persistent (systemd-networkd):
```bash
sudo nano /etc/systemd/network/can0.network
```
```ini
[Match]
Name=can0

[CAN]
BitRate=500000
DataBitRate=2000000
FDMode=yes
SamplePoint=0.75
RestartSec=100ms
```
```bash
sudo systemctl enable systemd-networkd
sudo systemctl restart systemd-networkd
```

---

## 10. GitHub Actions Self-Hosted Runner — Pending

```bash
mkdir actions-runner && cd actions-runner
# Download runner from:
# GitHub repo → Settings → Actions → Runners → New self-hosted runner
# Follow instructions for Linux ARM64
./config.sh --url https://github.com/<org>/<repo> --token <TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## Key Lessons Learned

| Issue | Root Cause | Fix |
|---|---|---|
| Flash timeout (90s → 400s) | 30 MB debug ELF too large | Auto-strip with `arm-none-eabi-objcopy --strip-debug` before flashing |
| `Verified OK` not found | `verify` removed from `program` command | Changed success check to `** Programming Finished **` |
| SWD clock capped at 3300 kHz | OpenOCD 0.11 + `dapdirect_swd` hardware limit | Accepted; OpenOCD 0.12 on Pi is inherently faster |
| SWD dropout mid-flash | Loose cable / power spike | Added `reset halt` before programming; reseat cable |
| `LIBUSB_ERROR_ACCESS` on Pi | Missing udev rules for STLINK | Copy `60-openocd.rules` to `/etc/udev/rules.d/` |
| `stlink-dap.cfg` deprecated | OpenOCD 0.12 dropped old interface | Switched to `interface/stlink.cfg` + `transport select swd` |
| Pi lost Wi-Fi after static IP | `dhcpcd.conf` not used on Bookworm | Use `nmcli` or router DHCP reservation |
| Flash 22s on Pi vs 400s on dev PC | OpenOCD 0.12 + direct USB + stripped ELF | Use Pi as the flash/test runner |
