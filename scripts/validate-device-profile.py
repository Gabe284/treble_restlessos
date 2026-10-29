#!/usr/bin/env python3
"""Validate the shape and safety invariants of a device observation profile.

This checker is deliberately read-only. It never accesses a phone or writes
partitions. It rejects profiles that accidentally enable flashing by default.
"""
import json
import sys
from pathlib import Path


REQUIRED_DEVICE_FIELDS = (
    "manufacturer",
    "marketing_name",
    "device_codename",
    "soc",
    "architecture",
)
REQUIRED_RUNTIME_FIELDS = (
    "system_android_release",
    "system_sdk",
    "vendor_android_release",
    "vendor_sdk",
    "active_slot_suffix",
)
REQUIRED_POLICY = (
    "profile_is_observation_only",
    "flash_allowed_by_profile",
    "automatic_firmware_replacement",
    "unknowns_must_fail_closed",
    "preserve_existing_device_patches",
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "devices/motorola/kansas/device.json"
    )
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")

    if profile.get("schema_version") != 1:
        fail("unsupported or missing schema_version")

    device = profile.get("device")
    runtime = profile.get("observed_runtime")
    policy = profile.get("policy")
    if not isinstance(device, dict) or not isinstance(runtime, dict):
        fail("device and observed_runtime must be JSON objects")
    if not isinstance(policy, dict):
        fail("policy must be a JSON object")

    for key in REQUIRED_DEVICE_FIELDS:
        if not device.get(key):
            fail(f"missing device.{key}")
    for key in REQUIRED_RUNTIME_FIELDS:
        if runtime.get(key) in (None, ""):
            fail(f"missing observed_runtime.{key}")
    for key in REQUIRED_POLICY:
        if key not in policy:
            fail(f"missing policy.{key}")

    if policy["profile_is_observation_only"] is not True:
        fail("device profile must remain observation-only")
    if policy["flash_allowed_by_profile"] is not False:
        fail("profile must not authorize flashing")
    if policy["automatic_firmware_replacement"] is not False:
        fail("automatic firmware replacement must remain disabled")
    if policy["unknowns_must_fail_closed"] is not True:
        fail("unknown conditions must fail closed")
    if policy["preserve_existing_device_patches"] is not True:
        fail("existing device patches must be preserved")

    if runtime["active_slot_suffix"] not in ("_a", "_b"):
        fail("active_slot_suffix must be _a or _b")
    if not isinstance(profile.get("verification", {}).get("unverified"), list):
        fail("verification.unverified must list outstanding checks")

    print(f"OK: {path} is structurally valid and remains non-flashing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
