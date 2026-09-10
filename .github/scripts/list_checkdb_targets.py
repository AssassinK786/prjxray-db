#!/usr/bin/env python3
"""
Enumerate one (db_root, part) pair per distinct device declared in each
family's mapping/devices.yaml, for a Vivado-free checkdb.py regression pass.

One representative part per *device* (not per fabric, and not all ~40-part
entries) is enough: checkdb.py's tile-overlap check depends only on which
fabric's tilegrid/segbits a part resolves to, and every part sharing a device
resolves to the same fabric. This also means a device that is misassigned to
the wrong device's fabric (the exact class of bug fixed in prjxray-db#15) is
still caught once per device, without the runtime cost of checking all ~40
parts individually.

Prints one line per target: "<family> <db_root_dir> <part>"
"""
import sys
import yaml
import pathlib

FAMILIES = ["artix7", "kintex7", "spartan7", "virtex7", "zynq7"]


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for family in FAMILIES:
        family_dir = root / family
        devices_yaml = family_dir / "mapping" / "devices.yaml"
        parts_yaml = family_dir / "mapping" / "parts.yaml"
        if not devices_yaml.exists() or not parts_yaml.exists():
            continue

        with open(devices_yaml) as f:
            devices = yaml.safe_load(f) or {}
        with open(parts_yaml) as f:
            parts = yaml.safe_load(f) or {}

        # One representative part per device: the first part.yaml entry
        # whose "device" field names it.
        part_for_device = {}
        for part_name, part_info in parts.items():
            dev = part_info.get("device")
            if dev and dev not in part_for_device:
                part_for_device[dev] = part_name

        for device in devices:
            part = part_for_device.get(device)
            if part is None:
                print(
                    f"WARNING: device '{device}' in {devices_yaml} has no "
                    f"part in {parts_yaml}",
                    file=sys.stderr,
                )
                continue
            print(f"{family} {family_dir} {part}")


if __name__ == "__main__":
    main()
