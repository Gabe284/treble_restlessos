#!/usr/bin/env python3
"""Validate Kansas kernel integration metadata and its non-flashing policy."""
import json
import sys
from pathlib import Path

DEFAULT_PATH = Path("devices/motorola/kansas/kernel-integration.json")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")

    if config.get("schema_version") != 1:
        fail("unsupported or missing schema_version")

    integration = config.get("integration")
    device = config.get("device")
    compatibility = config.get("compatibility")
    policy = config.get("policy")
    if not all(isinstance(value, dict) for value in (integration, device, compatibility, policy)):
        fail("integration, device, compatibility, and policy must be JSON objects")

    if integration.get("repository") != "Gabe284/GKI_KernelSU_SUSFS":
        fail("unexpected kernel source repository")
    if not integration.get("default_ref"):
        fail("integration.default_ref must be a non-empty reviewed source ref")
    if "android13-5.15" not in integration.get("android_gki_targets", []):
        fail("device baseline Android GKI target android13-5.15 must remain available")
    if not {"stable", "longterm", "mainline"}.issubset(set(integration.get("upstream_tracks", []))):
        fail("stable, longterm, and mainline tracks must all remain available")

    expected_device = {
        "manufacturer": "Motorola",
        "model": "XT2513-1",
        "codename": "kansas",
        "soc": "MediaTek MT6835",
        "observed_kernel": "5.15.208-android13-Wild",
    }
    for key, expected in expected_device.items():
        if device.get(key) != expected:
            fail(f"device.{key} must remain {expected!r}")

    for key in (
        "device_specific_kernel_source_confirmed",
        "vendor_module_kmi_verified",
        "avb_boot_acceptance_verified",
        "boot_recovery_path_verified",
        "flashable",
    ):
        if compatibility.get(key) is not False:
            fail(f"compatibility.{key} must remain false until independently verified")

    for key in (
        "automatic_kernel_replacement",
        "automatic_firmware_replacement",
        "include_kernel_in_gsi_system_image",
    ):
        if policy.get(key) is not False:
            fail(f"policy.{key} must remain false")

    if policy.get("preserve_existing_device_patches") is not True:
        fail("existing device patches must be preserved")
    if policy.get("fail_closed_on_unknowns") is not True:
        fail("unknown conditions must fail closed")

    print(f"OK: {path} preserves the non-flashing Kansas kernel integration policy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
