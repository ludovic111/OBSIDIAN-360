#!/usr/bin/env bash
set -u
out=/root/xbox-hardware-audit
mkdir -p "$out"
( uname -a; cat /proc/cpuinfo; cat /proc/meminfo; cat /proc/cmdline; cat /proc/version ) > "$out/cpu-memory.txt" 2>&1
( lspci -nnk; lspci -vvnn; cat /proc/iomem; cat /proc/ioports; cat /proc/interrupts ) > "$out/pci-resources.txt" 2>&1
( lsusb; lsusb -t; cat /proc/bus/input/devices; lsmod ) > "$out/usb-input-modules.txt" 2>&1
( lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS; findmnt; cat /etc/fstab; cat /proc/partitions ) > "$out/storage.txt" 2>&1
( ip -brief address; ip -s link show enp1s7; ethtool -i enp1s7; ethtool -k enp1s7; cat /etc/systemd/network/20-ethernet.network ) > "$out/network.txt" 2>&1
( cat /sys/class/graphics/fb0/name; cat /sys/class/graphics/fb0/virtual_size; cat /sys/class/graphics/fb0/bits_per_pixel; cat /sys/class/drm/card0-Unknown-1/modes; runuser -u xbox -- env DISPLAY=:0 XAUTHORITY=/home/xbox/.Xauthority xrandr --verbose; cat /proc/asound/cards; cat /proc/asound/pcm; ls -l /dev/smc* /dev/ana* /dev/mtd* /dev/dri/* 2>/dev/null ) > "$out/display-audio-platform.txt" 2>&1
( cat /etc/os-release; pacman -Q; systemctl --failed --no-pager; systemctl list-unit-files --state=enabled --no-pager ) > "$out/software.txt" 2>&1
dmesg > "$out/kernel-log.txt"
if test -e /proc/config.gz; then zcat /proc/config.gz > "$out/kernel.config"; fi
if test -d /sys/firmware/devicetree/base; then tar -C /sys/firmware/devicetree/base -czf "$out/device-tree.tar.gz" . 2>"$out/device-tree-copy.log"; fi
cp /home/xbox/.local/share/xorg/Xorg.0.log "$out/" 2>/dev/null || true
sha256sum /boot/vmlinuz-linux-xenon /boot/initramfs-linux-xenon.img > "$out/boot-files.sha256"
tar -C /root -czf /root/xbox-hardware-audit.tar.gz xbox-hardware-audit
printf 'AUDIT_COLLECTED\n'
