# Motorola Kansas (Moto G 2025) integration notes

## Confirmed runtime baseline

The checked-in `devices/motorola/kansas/device.json` records values observed from the running device on 2026-10-29. It is an observation record, not a flashing manifest.

- Marketing model: Moto G (2025), reported model XT2513-1 in prior device context.
- Vendor device/product: `kansas` / `kansas_g_vext`.
- SoC: MediaTek MT6835; architecture arm64.
- RestlessOS GSI: Android 16 / SDK 36.
- Motorola vendor stack: Android 13 / vendor SDK 33, build `W1VKS36H.9-12-1/62f8a3`.
- Kernel: `5.15.208-android13-Wild`.
- Active slot at capture: `_a`; `bootctl get-current-slot` and `bootctl get-active-boot-slot` both returned `0`.
- Dynamic partitions are present under `super`; observed logical partitions include system, vendor, product, system_ext, system_dlkm and vendor_dlkm.
- Vendor is mounted read-only as EROFS. Verity mapper devices were visible.
- Runtime properties reported verified boot state `green`, vbmeta device state `locked`, flash lock `1`, and AVB version `1.3`.

## Non-negotiable design boundary

RestlessOS is a GSI. Updating its system image does not update the Motorola vendor stack, kernel, modem, or other device firmware. The updater must represent these as separate artifact classes and must never describe a GSI-only update as a complete firmware update.

Do not replace `vendor`, `vendor_boot`, `boot`, `init_boot`, modem, trusted execution, connectivity, or other firmware partitions merely because a newer file exists. An artifact is eligible only when its exact model/region/carrier/build applicability, provenance, signature or published checksum, partition target, and rollback/recovery plan have been verified.

The current device reports a locked bootloader/AVB state. The integration must not assume that root access authorizes arbitrary flashing or that an unlocked/disabled-AVB procedure is an acceptable prerequisite. Support only a documented, verified update path appropriate to the actual device state; otherwise refuse writes and provide a diagnostic report.

## Existing compatibility work

- Keep all existing device compatibility patches intact unless a specific patch is reviewed against an identified upstream change.
- Do not bulk-copy upstream trees over this repository.
- Upstream syncs should be staged on a branch and reviewed as a diff.
- Preserve device-specific changes as small, documented patches where feasible.
- Require tests and a human-reviewed patch inventory before any patch removal or replacement.

## Runtime mount observations

The captured PID 1 mount table showed:

- `/vendor` is backed by `/dev/block/dm-7`, read-only EROFS.
- `/vendor/lib64/libmtk-ril.so` is a tmpfs mount at tmpfs root `/_vendor_lib64_libmtk-ril.so`.
- `/system/usr/keylayout` is a tmpfs mount at tmpfs root `/keylayout`.
- `/vendor/etc/usb_audio_policy_configuration.xml` is mounted from `/system/etc/usb_audio_policy_configuration.xml` on `/dev/block/dm-6`.

KernelSU appears to be installed: the process list included a `libksud.so` invocation and the root module directory exists. The module directory listed `meta-zeromount`, `susfs4ksu`, `zygisk_vector`, `sentry_radio_hardening`, and other modules. These observations do **not** prove which module or boot script created any individual mount. Do not attribute a mount to a module based on its name alone.

Before changing related files, inspect module metadata and scripts, init scripts, mount namespaces, overlay mechanisms, and actual backing files. Avoid printing secrets, private keys, tokens, or complete app data. Do not infer that changing the read-only EROFS image will change a separately mounted runtime file.

## Required checks before any installer can write

1. Confirm exact device model/variant and current Motorola build.
2. Collect read-only partition sizes, slot metadata, boot/AVB state, and image hashes.
3. Obtain an official Motorola package applicable to the exact variant and verify its provenance and integrity.
4. Compare the proposed artifact's declared target, size, hash, and build applicability against the device.
5. Verify the inactive slot is genuinely suitable for the intended update; never assume this from A/B naming alone.
6. Verify the recovery path and ensure user data and device-unique partitions are excluded.
7. Default to a dry run. Require explicit confirmation before any write.
8. Abort on unknown partitions, mismatched model/build, missing hashes, failed signature checks, or incomplete recovery information.
9. Do not treat a reported green/locked state as independent verification by this repository; preserve the raw observations and their provenance.
10. Do not enable firmware writes while the bootloader/update path and recovery procedure are unresolved.

## Current status

This profile is read-only and does not authorize flashing. Observed partition sizes and slot metadata are recorded in the device profile. Image hashes, inactive-slot completeness/bootability, exact origin of runtime mount overlays, official Motorola firmware package identity, and a verified write-capable update path remain unverified. No firmware binaries or proprietary blobs are included.
