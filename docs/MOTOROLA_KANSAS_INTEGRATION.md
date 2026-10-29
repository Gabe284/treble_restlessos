# Motorola Kansas (Moto G 2025) integration notes

## Confirmed runtime baseline

The checked-in `devices/motorola/kansas/device.json` records values observed from the running device on 2026-10-29. It is an observation record, not a flashing manifest.

- Marketing model: Moto G (2025), reported model XT2513-1 in prior device context.
- Vendor device/product: `kansas` / `kansas_g_vext`.
- SoC: MediaTek MT6835; architecture arm64.
- RestlessOS GSI: Android 16 / SDK 36.
- Motorola vendor stack: Android 13 / vendor SDK 33, build `W1VKS36H.9-12-1/62f8a3`.
- Kernel: `5.15.208-android13-Wild`.
- Active slot at capture: `_a`.
- Dynamic partitions are present under `super`; observed logical partitions include system, vendor, product, system_ext, system_dlkm and vendor_dlkm.
- Vendor is mounted read-only as EROFS. Verity mapper devices were visible.

## Non-negotiable design boundary

RestlessOS is a GSI. Updating its system image does not update the Motorola vendor stack, kernel, modem, or other device firmware. The updater must represent these as separate artifact classes and must never describe a GSI-only update as a complete firmware update.

Do not replace `vendor`, `vendor_boot`, `boot`, `init_boot`, modem, trusted execution, connectivity, or other firmware partitions merely because a newer file exists. An artifact is eligible only when its exact model/region/carrier/build applicability, provenance, signature or published checksum, partition target, and rollback/recovery plan have been verified.

## Existing compatibility work

- Keep all existing device compatibility patches intact unless a specific patch is reviewed against an identified upstream change.
- Do not bulk-copy upstream trees over this repository.
- Upstream syncs should be staged on a branch and reviewed as a diff.
- Preserve device-specific changes as small, documented patches where feasible.
- Require tests and a human-reviewed patch inventory before any patch removal or replacement.

## Runtime mount observations

The captured `mount` output showed `/vendor/lib64/libmtk-ril.so`, `/vendor/etc/usb_audio_policy_configuration.xml`, and `/system/usr/keylayout` mounted separately, including tmpfs mounts. This does not identify their source or persistence mechanism. Before changing any related files, inspect mount namespaces, init scripts, Magisk/KernelSU modules, overlay mechanisms, and the actual backing files. Do not infer that changing the read-only EROFS image will change the mounted runtime file.

## Required checks before any installer can write

1. Confirm exact device model/variant and current Motorola build.
2. Collect read-only partition sizes, slot metadata, boot/AVB state, and image hashes.
3. Obtain an official Motorola package applicable to the exact variant and verify its provenance and integrity.
4. Compare the proposed artifact's declared target, size, hash, and build applicability against the device.
5. Verify the inactive slot is genuinely suitable for the intended update; never assume this from A/B naming alone.
6. Verify the recovery path and ensure user data and device-unique partitions are excluded.
7. Default to a dry run. Require explicit confirmation before any write.
8. Abort on unknown partitions, mismatched model/build, missing hashes, failed signature checks, or incomplete recovery information.

## Current status

This profile is read-only and does not authorize flashing. Partition sizes, image hashes, AVB/bootloader state, inactive-slot health, official firmware package identity, and the source of runtime mount overlays remain unverified. No firmware binaries or proprietary blobs are included.
