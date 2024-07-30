#!/usr/bin/env python3
# Copyright © 2024 Bitcrush Testing

import argparse
import os
import socket
import logging
# Suppress Scapy IPv6 warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import ARP, Ether, srp, conf


# Define MAC address prefixes for Raspberry Pi
RASPBERRY_PI_MAC_PREFIXES = ["b8:27:eb", "dc:a6:32"]

def is_raspberry_pi(mac):
    """
    Checks if a given MAC address belongs to a Raspberry Pi
    """
    mac_prefix = mac.lower()[:8]
    return mac_prefix in RASPBERRY_PI_MAC_PREFIXES

def get_hostname(ip):
    """
    Returns the hostname for `ip` if it can be resolved
    """
    try:
        hostname = socket.gethostbyaddr(ip)
        return hostname[0]
    except socket.herror:
        return None

def scan_network(network_prefix, hostname_filter=None):
    """
    Scans the network for devices and filters Raspberry Pis
    """
    arp_request = ARP(pdst=network_prefix)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []
    for sent, received in answered_list:
        ip = received.psrc
        mac = received.hwsrc
        if is_raspberry_pi(mac):
            hostname = get_hostname(ip)
            if hostname_filter:
                if hostname and hostname_filter in hostname:
                    devices.append({'ip': ip, 'hostname': hostname})
            else:
                devices.append({'ip': ip, 'hostname': hostname})

    return devices

def write_inventory_file(devices, filename="inventory.ini"):
    """
    Writes the discovered devices to an Ansible inventory file
    """
    with open(filename, 'w') as f:
        f.write("[raspberry_pi]\n")
        for device in devices:
            line = f"{device['ip']}"
            if device['hostname']:
                line += f" ansible_host={device['hostname']}"
            f.write(line + "\n")

def check_sudo():
    """
    Checks if the script is run with sudo
    """
    if os.geteuid() != 0:
        print("This script must be run with sudo.")
        sys.exit(1)

def main():
    check_sudo()

    parser = argparse.ArgumentParser(description="Scan network for Raspberry Pis for Ansible inventory")
    parser.add_argument("network_prefix", help="IP range to scan (e.g., 192.168.1.0/24)")
    parser.add_argument("--hostname-filter", help="Optional filter for hostnames")
    parser.add_argument("--output", default="inventory.ini", help="Output file name (default: inventory.ini)")

    args = parser.parse_args()

    devices = scan_network(args.network_prefix, args.hostname_filter)
    write_inventory_file(devices, args.output)
    print(f"Inventory written to {args.output}")

if __name__ == "__main__":
    main()

